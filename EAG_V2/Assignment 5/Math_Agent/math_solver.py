# orchestrator.py
# Uses Gemini 2.0 Flash function-calling to:
#  - Solve a multi-step problem (>=6 steps), each as a tool call via MCP
#  - Validate the result
#  - Send Telegram message with question + answer
#  - Finally, print ONLY the final numeric answer
#
# Usage:
#   python orchestrator.py "Compute: ((3/4) + (5/6)) * (7 - (2 + 9/3))^2 + 15 / (3 * (2 + 1))"
#   # or just: python orchestrator.py    (uses a default problem)
from __future__ import annotations

import asyncio
import os
import sys
from typing import Dict, Any, List

from dotenv import load_dotenv
load_dotenv()

# --- Gemini (Google GenAI Python SDK) ---
from google.genai import Client as GenAIClient
from google.genai import types as gg

# --- MCP client (stdio transport) ---
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SYSTEM_INSTRUCTION = """
You are a math-solving agent. Your rules:
1) PREFER evaluate_expression for most problems - it can handle complex expressions in ONE call.
2) Only use step_add, step_subtract, step_multiply, step_divide, step_power for multi-step explanations.
3) When you have a final answer, call check_answer ONCE to verify it.
4) After verification, respond with ONLY the final numeric answer (no other text).
5) Do NOT call send_telegram unless explicitly requested.
6) MINIMIZE API calls - use the fewest tools possible.

Example for "2 + 3":
- Call: evaluate_expression(expr="2 + 3")  → returns 5
- Call: check_answer(verifier_expression="2 + 3", final_answer=5)
- Response: "5"

Example for complex: "((3/4) + (5/6)) * (7 - (2 + 9/3))^2":
- Call: evaluate_expression(expr="((3/4) + (5/6)) * (7 - (2 + 9/3))**2")
- Call: check_answer(...) 
- Response: "<result>"
"""

# Function declarations for Gemini (mirror MCP tools)
def function_declarations() -> gg.Tool:
    def fn(name: str, desc: str, props: Dict[str, Any], required: List[str]) -> gg.FunctionDeclaration:
        return gg.FunctionDeclaration(
            name=name,
            description=desc,
            parameters=gg.Schema(type="OBJECT", properties=props, required=required),
        )

    fns = [
        fn("step_add", "Add two numbers as a single step.",
           {"a": gg.Schema(type="NUMBER"), "b": gg.Schema(type="NUMBER"), "note": gg.Schema(type="STRING")},
           ["a", "b"]),
        fn("step_subtract", "Subtract b from a as a single step.",
           {"a": gg.Schema(type="NUMBER"), "b": gg.Schema(type="NUMBER"), "note": gg.Schema(type="STRING")},
           ["a", "b"]),
        fn("step_multiply", "Multiply two numbers as a single step.",
           {"a": gg.Schema(type="NUMBER"), "b": gg.Schema(type="NUMBER"), "note": gg.Schema(type="STRING")},
           ["a", "b"]),
        fn("step_divide", "Divide a by b as a single step.",
           {"a": gg.Schema(type="NUMBER"), "b": gg.Schema(type="NUMBER"), "note": gg.Schema(type="STRING")},
           ["a", "b"]),
        fn("step_power", "Compute base^exponent as a single step.",
           {"base": gg.Schema(type="NUMBER"), "exponent": gg.Schema(type="NUMBER"), "note": gg.Schema(type="STRING")},
           ["base", "exponent"]),
        fn("simplify_expression", "Simplify a string math expression.",
           {"expression": gg.Schema(type="STRING")}, ["expression"]),
        fn("evaluate_expression", "Evaluate a numeric expression string.",
           {"expression": gg.Schema(type="STRING")}, ["expression"]),
        fn("check_answer", "Validate final answer by re-evaluating verifier_expression and comparing to final_answer within tolerance.",
           {"verifier_expression": gg.Schema(type="STRING"),
            "final_answer": gg.Schema(type="NUMBER"),
            "tolerance": gg.Schema(type="NUMBER")}, ["verifier_expression", "final_answer"]),
        fn("send_telegram", "Send the question and final answer via Telegram using env credentials on the MCP server.",
           {"message": gg.Schema(type="STRING")}, ["message"]),
    ]
    return gg.Tool(function_declarations=fns)

async def connect_mcp(server_script_path: str):
    """
    Launch the MCP server over stdio and return a connected ClientSession.
    Returns an async context manager that yields (read, write, session).
    """
    params = StdioServerParameters(command="python3", args=[server_script_path], env=None)
    return stdio_client(params)

async def run():
    problem = " ".join(sys.argv[1:]).strip() or \
        "Compute: ((3/4) + (5/6)) * (7 - (2 + 9/3))^2 + 15 / (3 * (2 + 1))"

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in environment")

    # 1) Connect to MCP server (spawns our math server over stdio)
    stdio_cm = await connect_mcp("mcp_math_server.py")
    
    async with stdio_cm as (read, write):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            
            # Optional: list tools for visibility
            tools = await mcp_session.list_tools()
            print("MCP tools:", [t.name for t in tools.tools])

            # 2) Prepare Gemini client + config
            client = GenAIClient(api_key=gemini_api_key)

            tool = function_declarations()
            cfg = gg.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[tool],
                # Force tool usage whenever the model wants (and allow multi-tool turns)
                tool_config=gg.ToolConfig(
                    function_calling_config=gg.FunctionCallingConfig(mode="ANY")
                ),
                temperature=0.2,
                max_output_tokens=2048,
            )

            # 3) Start the conversation
            contents: list[gg.Content] = [
                gg.Content(role="user", parts=[gg.Part(text=problem)])
            ]

            final_text: str = ""

            while True:
                resp = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001"),
                    contents=contents,
                    config=cfg,
                )

                # If the model decided to call functions, handle them
                fcs = getattr(resp, "function_calls", None) or []
                if not fcs:
                    # No function calls; treat as final text
                    final_text = (resp.text or "").strip()
                    break

                # Gemini can emit multiple function calls in one turn
                # We will execute each via MCP, then append function_response parts.
                contents.append(resp.candidates[0].content)  # preserve the function_call part(s)
                for fc in fcs:
                    name = fc.name
                    args = dict(fc.function_call.args) if hasattr(fc, "function_call") else {}
                    # Call MCP tool
                    result = await mcp_session.call_tool(name, args)
                    # The MCP SDK returns a ToolResponse; we want its "content" or structured data
                    # We'll pass structured content back to Gemini:
                    structured = {}
                    try:
                        # result.content may already be a list of text parts with JSON
                        if result.content:
                            # Each item can be text; prefer structuredContent if present
                            # The fastmcp helper in our server returns "structuredContent" in the text body as JSON too.
                            text = result.content[0].text if hasattr(result.content[0], "text") else None
                            if text:
                                structured = json.loads(text)
                    except Exception:
                        structured = {"raw": str(result.content)}

                    # Provide function response back to Gemini
                    contents.append(
                        gg.Content(
                            role="tool",
                            parts=[gg.Part.from_function_response(name=name, response=structured)]
                        )
                    )

            # 4) Print ONLY the final numeric answer (the system instruction enforces this)
            print(final_text)

if __name__ == "__main__":
    import json
    asyncio.run(run())
