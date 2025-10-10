import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import google.generativeai as genai
import asyncio
from rich.console import Console
from rich.panel import Panel
import sys

console = Console()

# Load environment variables and setup Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

async def generate_with_timeout(client, prompt, timeout=30):
    """Generate content with a timeout"""
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.generate_content(prompt)
            ),
            timeout=timeout
        )
        return response
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None

async def main():
    try:
        console.print(Panel("Math Problem Solver", border_style="cyan"))

        server_params = StdioServerParameters(
            command="python3",
            args=["mcp_math_server.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                system_prompt = """You are a step-by-step mathematical reasoning agent designed to solve problems accurately using tools.

                                    TOOLS AVAILABLE:
                                    1. evaluate_expression(expr: str) → Evaluate math expressions.
                                    2. check_answer(verifier_expression: str, final_answer: float) → Verify correctness.

                                    ---

                                    ### CORE INSTRUCTIONS
                                    1. **Think before you act.** First, read the problem carefully. Write out your reasoning step-by-step (Reasoning Phase).  
                                    2. **Tool Phase.** Use tools only after finishing your reasoning.  
                                    - Call `evaluate_expression` when ready to compute the full or partial expression.  
                                    - After receiving a result, verify it by calling `check_answer`.  
                                    3. **Verification Phase.** If verification fails, explain the issue and recompute.  
                                    4. **Final Phase.** End with one final line showing only the confirmed answer.

                                    ---

                                    ### OUTPUT FORMAT (MUST FOLLOW EXACTLY)
                                    Each message must contain exactly one of the following:
                                    - `REASONING:` followed by numbered logical steps.
                                    - `FUNCTION_CALL: function_name|param1|param2|...`
                                    - `FUNCTION_RESPONSE:` followed by the returned value from the tool.
                                    - `SELF_CHECK:` followed by your validation or correction reasoning.
                                    - `FINAL_ANSWER: [answer]`

                                    ---

                                    ### EXAMPLE WORKFLOW
                                    User: Solve (3 + 5) * 2  

                                    Assistant:
                                    REASONING:  
                                    1. Identify operation inside parentheses: 3 + 5 = 8  
                                    2. Multiply result by 2 → expression = 8 * 2  

                                    FUNCTION_CALL: evaluate_expression|(3 + 5) * 2  

                                    User: Result is 16.  

                                    Assistant:
                                    FUNCTION_CALL: check_answer|(3 + 5) * 2|16  

                                    User: Verification OK.  

                                    Assistant:
                                    SELF_CHECK: Verified successfully.  
                                    FINAL_ANSWER: [16]

                                    ---

                                    ### ERROR & UNCERTAINTY HANDLING
                                    - If a tool call fails or returns an unexpected value, write:
                                    `SELF_CHECK: Error detected – re-evaluating.`
                                    - Re-run the correct tool with corrected inputs.
                                    - Never skip verification or self-check.
                                    - If unsure, ask for clarification before finalizing.

                                    ---

                                    ### REASONING TAGGING
                                    Whenever reasoning is written, label each step with the type of reasoning:
                                    - (Arithmetic), (Logic), (Simplification), (Verification)

                                    ---

                                    ### SUMMARY
                                    - Always reason → compute → verify → finalize.
                                    - Never call a tool without prior reasoning.
                                    - Always confirm correctness before `FINAL_ANSWER`.
                                    - Use the exact structured format above in every response."""

                problem = " ".join(sys.argv[1:]).strip() or "((3/4) + (5/6)) * (7 - (2 + 9/3))^2 + 15 / (3 * (2 + 1))"
                console.print(Panel(f"Problem: {problem}", border_style="cyan"))

                # Initialize conversation
                prompt = f"{system_prompt}\n\nSolve this problem step by step: {problem}"
                conversation_history = []
                executed_calls = set()  # Prevent duplicate tool invocations
                
                # Initialize Gemini client
                client = genai.GenerativeModel('gemini-2.0-flash')

                while True:
                    response = await generate_with_timeout(client, prompt)
                    if not response or not response.text:
                        break

                    result = response.text.strip()
                    console.print(f"\n[yellow]A:[/yellow] {result}")

                    # Parse lines in order, handling function calls and final answer
                    lines = result.split('\n')
                    processed_function = False
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Skip lines that look like conversation continuations
                        if line.startswith("User:") or line.startswith("Assistant:"):
                            continue
                        
                        # If we see FINAL_ANSWER, process it immediately regardless of what else happened
                        if line.startswith("FINAL_ANSWER:"):
                            # Extract and display the final answer
                            final_answer = line.split("[")[1].split("]")[0]
                            console.print(f"\n[green bold]Final Answer: {final_answer}[/green bold]")
                            
                            # Send result via Telegram
                            telegram_message = f"Math Problem: {problem}\nAnswer: {final_answer}"
                            try:
                                telegram_result = await session.call_tool("send_telegram", arguments={"message": telegram_message})
                                if telegram_result.content:
                                    telegram_status = telegram_result.content[0].text
                                    console.print(f"[cyan]Telegram: {telegram_status}[/cyan]")
                            except Exception as e:
                                console.print(f"[yellow]Telegram notification skipped: {e}[/yellow]")
                            
                            console.print("\n[green]Calculation completed![/green]")
                            return
                        
                        # Skip additional function calls if we already processed one
                        if processed_function:
                            continue
                            
                        if line.startswith("FUNCTION_CALL:"):
                            _, function_info = line.split(":", 1)
                            parts = [p.strip() for p in function_info.split("|")]
                            func_name = parts[0]
                            call_key = f"{func_name}|{'|'.join(parts[1:])}"

                            # Skip duplicate calls entirely
                            if call_key in executed_calls:
                                processed_function = True
                                continue
                            
                            if func_name == "evaluate_expression":
                                expression = parts[1]
                                calc_result = await session.call_tool("evaluate_expression", arguments={"expr": expression})
                                if calc_result.content:
                                    value = calc_result.content[0].text
                                    prompt += f"\nUser: Result is {value}. Let's verify."
                                    conversation_history.append((expression, float(value)))
                                executed_calls.add(call_key)
                                processed_function = True
                                    
                            elif func_name == "check_answer":
                                expression, expected = parts[1], float(parts[2])
                                await session.call_tool("check_answer", arguments={
                                    "verifier_expression": expression,
                                    "final_answer": expected
                                })
                                prompt += f"\nUser: Verified correct."
                                executed_calls.add(call_key)
                                processed_function = True
                                
                            elif func_name == "step_add":
                                a, b = float(parts[1]), float(parts[2])
                                calc_result = await session.call_tool("step_add", arguments={"a": a, "b": b})
                                if calc_result.content:
                                    value = calc_result.content[0].text
                                    prompt += f"\nUser: Result is {value}."
                                    conversation_history.append((f"{a} + {b}", float(value)))
                                executed_calls.add(call_key)
                                processed_function = True
                                    
                            elif func_name == "step_subtract":
                                a, b = float(parts[1]), float(parts[2])
                                calc_result = await session.call_tool("step_subtract", arguments={"a": a, "b": b})
                                if calc_result.content:
                                    value = calc_result.content[0].text
                                    prompt += f"\nUser: Result is {value}."
                                    conversation_history.append((f"{a} - {b}", float(value)))
                                executed_calls.add(call_key)
                                processed_function = True
                                    
                            elif func_name == "step_multiply":
                                a, b = float(parts[1]), float(parts[2])
                                calc_result = await session.call_tool("step_multiply", arguments={"a": a, "b": b})
                                if calc_result.content:
                                    value = calc_result.content[0].text
                                    prompt += f"\nUser: Result is {value}."
                                    conversation_history.append((f"{a} * {b}", float(value)))
                                executed_calls.add(call_key)
                                processed_function = True
                                    
                            elif func_name == "step_divide":
                                a, b = float(parts[1]), float(parts[2])
                                calc_result = await session.call_tool("step_divide", arguments={"a": a, "b": b})
                                if calc_result.content:
                                    value = calc_result.content[0].text
                                    prompt += f"\nUser: Result is {value}."
                                    conversation_history.append((f"{a} / {b}", float(value)))
                                executed_calls.add(call_key)
                                processed_function = True
                                    
                            elif func_name == "step_power":
                                base, exponent = float(parts[1]), float(parts[2])
                                calc_result = await session.call_tool("step_power", arguments={"base": base, "exponent": exponent})
                                if calc_result.content:
                                    value = calc_result.content[0].text
                                    prompt += f"\nUser: Result is {value}."
                                    conversation_history.append((f"{base} ^ {exponent}", float(value)))
                                executed_calls.add(call_key)
                                processed_function = True
                                    
                            elif func_name == "simplify_expression":
                                expression = parts[1]
                                calc_result = await session.call_tool("simplify_expression", arguments={"expr": expression})
                                if calc_result.content:
                                    value = calc_result.content[0].text
                                    prompt += f"\nUser: Simplified to {value}."
                                executed_calls.add(call_key)
                                processed_function = True

                    # Keep prompt minimal; no extra assistant echoes to avoid repetition

                console.print("\n[green]Calculation completed![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
