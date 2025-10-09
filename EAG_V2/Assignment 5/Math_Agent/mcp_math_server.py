from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from rich.console import Console
from rich.panel import Panel
import sys
from sympy import sympify, N as sympy_eval
import os
from dotenv import load_dotenv
import requests

# Use stderr for console output to avoid interfering with JSON-RPC on stdout
console = Console(file=sys.stderr)
mcp = FastMCP("MathSolver")
load_dotenv()

@mcp.tool()
def evaluate_expression(expr: str) -> TextContent:
    """Evaluate any mathematical expression"""
    console.print("[blue]FUNCTION CALL:[/blue] evaluate_expression()")
    console.print(f"[blue]Expression:[/blue] {expr}")
    try:
        # Use sympy for safe evaluation
        result = float(sympy_eval(sympify(expr)))
        console.print(f"[green]Result:[/green] {result}")
        return TextContent(
            type="text",
            text=str(result)
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )

@mcp.tool()
def check_answer(verifier_expression: str, final_answer: float) -> TextContent:
    """Verify if the calculated answer is correct"""
    console.print("[blue]FUNCTION CALL:[/blue] check_answer()")
    console.print(f"[blue]Verifying:[/blue] {verifier_expression} = {final_answer}")
    try:
        actual = float(sympy_eval(sympify(verifier_expression)))
        is_correct = abs(actual - float(final_answer)) < 1e-10
        
        if is_correct:
            console.print(f"[green]✓ Correct! {verifier_expression} = {final_answer}[/green]")
        else:
            console.print(f"[red]✗ Incorrect! {verifier_expression} should be {actual}, got {final_answer}[/red]")
            
        return TextContent(
            type="text",
            text=str(is_correct)
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )

@mcp.tool()
def step_add(a: float, b: float) -> TextContent:
    """Add two numbers"""
    console.print("[blue]FUNCTION CALL:[/blue] step_add()")
    result = a + b
    console.print(f"[blue]Calculation:[/blue] {a} + {b} = {result}")
    return TextContent(type="text", text=str(result))

@mcp.tool()
def step_subtract(a: float, b: float) -> TextContent:
    """Subtract two numbers"""
    console.print("[blue]FUNCTION CALL:[/blue] step_subtract()")
    result = a - b
    console.print(f"[blue]Calculation:[/blue] {a} - {b} = {result}")
    return TextContent(type="text", text=str(result))

@mcp.tool()
def step_multiply(a: float, b: float) -> TextContent:
    """Multiply two numbers"""
    console.print("[blue]FUNCTION CALL:[/blue] step_multiply()")
    result = a * b
    console.print(f"[blue]Calculation:[/blue] {a} * {b} = {result}")
    return TextContent(type="text", text=str(result))

@mcp.tool()
def step_divide(a: float, b: float) -> TextContent:
    """Divide two numbers"""
    console.print("[blue]FUNCTION CALL:[/blue] step_divide()")
    if b == 0:
        console.print("[red]Error: Division by zero[/red]")
        return TextContent(type="text", text="Error: Division by zero")
    result = a / b
    console.print(f"[blue]Calculation:[/blue] {a} / {b} = {result}")
    return TextContent(type="text", text=str(result))

@mcp.tool()
def step_power(base: float, exponent: float) -> TextContent:
    """Raise a number to a power"""
    console.print("[blue]FUNCTION CALL:[/blue] step_power()")
    result = base ** exponent
    console.print(f"[blue]Calculation:[/blue] {base} ^ {exponent} = {result}")
    return TextContent(type="text", text=str(result))

@mcp.tool()
def simplify_expression(expr: str) -> TextContent:
    """Simplify an algebraic expression"""
    console.print("[blue]FUNCTION CALL:[/blue] simplify_expression()")
    console.print(f"[blue]Expression:[/blue] {expr}")
    try:
        from sympy import simplify
        result = str(simplify(sympify(expr)))
        console.print(f"[green]Simplified:[/green] {result}")
        return TextContent(type="text", text=result)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(type="text", text=f"Error: {str(e)}")

@mcp.tool()
def send_telegram(message: str) -> TextContent:
    """Send a message via Telegram (optional)"""
    console.print("[blue]FUNCTION CALL:[/blue] send_telegram()")
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id:
            console.print("[yellow]Warning: Telegram credentials not configured[/yellow]")
            return TextContent(type="text", text="Telegram not configured")
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=20)
        
        if response.ok:
            console.print("[green]✓ Message sent via Telegram[/green]")
            return TextContent(type="text", text="Message sent successfully")
        else:
            console.print(f"[red]Failed to send: {response.status_code}[/red]")
            return TextContent(type="text", text=f"Failed: {response.status_code}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(type="text", text=f"Error: {str(e)}")

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
