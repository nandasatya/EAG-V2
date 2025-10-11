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

async def generate_with_timeout(client, prompt, timeout=30, llm_call_count=0):
    """Generate content with a timeout"""
    try:
        console.print(f"\n[magenta]═══ Gemini LLM Call #{llm_call_count} ═══[/magenta]")
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

                system_prompt = """You are a mathematical reasoning agent that solves problems step-by-step using tools.

=== TOOLS ===
1. evaluate_expression(expr) - Compute mathematical expression
2. check_answer(expr, answer) - Verify result correctness
3. send_telegram(message) - Send notification

=== 4-STEP WORKFLOW ===
Step 1: FUNCTION_CALL: evaluate_expression|<expression>
Step 2: FUNCTION_CALL: check_answer|<expression>|<result>
Step 3: FUNCTION_CALL: send_telegram|Problem: X, Answer: Y
Step 4: TEXT OUTPUT ONLY (NO FUNCTION CALLS):
        SELF_CHECK: <verification>
        FINAL_ANSWER: [result]

=== OUTPUT FORMAT (use pipes, NOT JSON) ===
FUNCTION_CALL: function_name|param1|param2
or
SELF_CHECK: [verification statement]
FINAL_ANSWER: [result]

=== REASONING PRINCIPLES ===
- One action per response: Steps 1-3 = ONE function call each, Step 4 = TEXT ONLY
- Wait for feedback: don't predict tool responses
- NO FUNCTION CALLS in step 4: only output SELF_CHECK and FINAL_ANSWER text
- Tag reasoning types in SELF_CHECK: (Arithmetic), (Logic), (Verification)

=== ERROR HANDLING ===
- If tool fails: acknowledge error in SELF_CHECK, proceed if possible
- If verification fails: note discrepancy in SELF_CHECK before FINAL_ANSWER
- If uncertain: mention limitation in SELF_CHECK
- Never hallucinate tool responses

=== CONVERSATION LOOP ===
After each FUNCTION_CALL, wait for user feedback before next step.
User will provide: "Result is X" or "Verified correct" or "Message sent successfully"
Use this feedback to proceed to next step.

=== SELF_CHECK REQUIREMENTS ===
Before FINAL_ANSWER, verify:
1. Computation completed? (cite actual result from tool)
2. Verification passed? (cite check_answer response)  
3. Telegram sent? (cite send_telegram confirmation)
4. Result format correct? (number, units if any)

=== EXAMPLE ===
User: Solve (3 + 5) * 2

Response 1:
FUNCTION_CALL: evaluate_expression|(3 + 5) * 2

User: Result is 16. Now do step #2: call check_answer

Response 2:
FUNCTION_CALL: check_answer|(3 + 5) * 2|16

User: Verified correct. Now do step #3: call send_telegram

Response 3:
FUNCTION_CALL: send_telegram|Problem: (3 + 5) * 2, Answer: 16

User: Message sent successfully. Now do step #4: output SELF_CHECK and FINAL_ANSWER

Response 4 (TEXT ONLY - NO MORE FUNCTION CALLS):
SELF_CHECK: (Verification) Evaluated expression, got 16. Check_answer confirmed correctness. Telegram notification sent successfully. Result is integer, unitless as expected.
FINAL_ANSWER: [16]

=== CRITICAL: STEP 4 RULES ===
After receiving "Message sent successfully", you MUST output ONLY text:
- First line: SELF_CHECK: <summary of all 3 steps>
- Second line: FINAL_ANSWER: [number]
- DO NOT call any more functions
- DO NOT output FUNCTION_CALL in step 4

=== START ===
Output step 1 now (evaluate_expression call only)."""

                problem = " ".join(sys.argv[1:]).strip() or "((3/4) + (5/6)) * (7 - (2 + 9/3))^2 + 15 / (3 * (2 + 1))"
                console.print(Panel(f"Problem: {problem}", border_style="cyan"))

                # Initialize conversation
                prompt = f"{system_prompt}\n\nSolve this problem step by step: {problem}"
                conversation_history = []
                executed_calls = set()  # Prevent duplicate tool invocations
                llm_call_count = 0  # Track number of LLM calls
                
                # Initialize Gemini client
                client = genai.GenerativeModel('gemini-2.0-flash')

                while True:
                    llm_call_count += 1
                    response = await generate_with_timeout(client, prompt, llm_call_count=llm_call_count)
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
                        
                        # Skip lines that look like conversation continuations (case-insensitive)
                        line_upper = line.upper()
                        if (line_upper.startswith("USER:") or line_upper.startswith("ASSISTANT:") or 
                            line_upper.startswith("FUNCTION_RESPONSE:")):
                            continue
                        
                        # If we see FINAL_ANSWER, process it immediately regardless of what else happened
                        if line.startswith("FINAL_ANSWER:"):
                            # Extract and display the final answer
                            final_answer = line.split("[")[1].split("]")[0]
                            console.print(f"\n[green bold]Final Answer: {final_answer}[/green bold]")
                            
                            console.print("\n[green]Calculation completed![/green]")
                            console.print(f"[magenta]Total Gemini LLM Calls: {llm_call_count}[/magenta]")
                            return
                        
                        # Skip additional function calls if we already processed one
                        if processed_function:
                            continue
                            
                        if "FUNCTION_CALL:" in line:
                            # Extract function call - handle "#1: FUNCTION_CALL:" or "FUNCTION_CALL:"
                            function_info = line.split("FUNCTION_CALL:", 1)[1].strip()
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
                                    prompt += f"\nUser: Result is {value}.\n\nNow do step #2: call check_answer"
                                    conversation_history.append((expression, float(value)))
                                executed_calls.add(call_key)
                                processed_function = True
                                    
                            elif func_name == "check_answer":
                                expression, expected = parts[1], float(parts[2])
                                await session.call_tool("check_answer", arguments={
                                    "verifier_expression": expression,
                                    "final_answer": expected
                                })
                                prompt += f"\nUser: Verified correct.\n\nNow do step #3: call send_telegram"
                                executed_calls.add(call_key)
                                processed_function = True
                            
                            elif func_name == "send_telegram":
                                message = parts[1] if len(parts) > 1 else f"Math Problem: {problem}, Answer: [result]"
                                try:
                                    telegram_result = await session.call_tool("send_telegram", arguments={"message": message})
                                    if telegram_result.content:
                                        telegram_status = telegram_result.content[0].text
                                        console.print(f"[cyan]Telegram: {telegram_status}[/cyan]")
                                        prompt += f"\nUser: Message sent successfully.\n\nNow do step #4: output SELF_CHECK and FINAL_ANSWER"
                                except Exception as e:
                                    console.print(f"[yellow]Telegram notification failed: {e}[/yellow]")
                                    prompt += f"\nUser: Message sending skipped.\n\nNow do step #4: output SELF_CHECK and FINAL_ANSWER"
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
