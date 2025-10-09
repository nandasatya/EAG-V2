# mcp_math_server.py
# An MCP server (stdio transport) exposing math step tools + validation + Telegram sender.
# Run on stdio (spawned by orchestrator), or develop with: `python mcp_math_server.py`
from __future__ import annotations

import os
import json
import requests
from decimal import Decimal, getcontext
from dataclasses import asdict
from typing import Optional

from mcp.server.fastmcp import FastMCP
from sympy import sympify, simplify as sym_simplify  # safe expression parsing
from sympy.core.numbers import Float as SymFloat
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("math-tools-server")

# Use higher precision for floating arithmetic (you can tweak if needed)
getcontext().prec = 50


def _ret(payload: dict):
    """
    MCP tools can just return Python values. For extra structure/debuggability
    we also provide a JSON string in case a client wants to read it as text.
    """
    return {
        "content": [{"type": "text", "text": json.dumps(payload)}],
        "structuredContent": payload,
    }

# ---------- Atomic Math Step Tools ----------
@mcp.tool()
def step_add(a: float, b: float, note: Optional[str] = None) -> dict:
    """Add two numbers as one atomic step."""
    res = float(Decimal(str(a)) + Decimal(str(b)))
    return _ret({"result": res, "step": f"{a} + {b} = {res}", "note": note})

@mcp.tool()
def step_subtract(a: float, b: float, note: Optional[str] = None) -> dict:
    """Subtract b from a as one atomic step."""
    res = float(Decimal(str(a)) - Decimal(str(b)))
    return _ret({"result": res, "step": f"{a} - {b} = {res}", "note": note})

@mcp.tool()
def step_multiply(a: float, b: float, note: Optional[str] = None) -> dict:
    """Multiply a*b as one atomic step."""
    res = float(Decimal(str(a)) * Decimal(str(b)))
    return _ret({"result": res, "step": f"{a} * {b} = {res}", "note": note})

@mcp.tool()
def step_divide(a: float, b: float, note: Optional[str] = None) -> dict:
    """Divide a by b as one atomic step."""
    if b == 0:
        return _ret({"error": "Division by zero"})
    res = float(Decimal(str(a)) / Decimal(str(b)))
    return _ret({"result": res, "step": f"{a} / {b} = {res}", "note": note})

@mcp.tool()
def step_power(base: float, exponent: float, note: Optional[str] = None) -> dict:
    """Compute base^exponent as one atomic step."""
    res = float(Decimal(str(base)) ** Decimal(str(exponent)))
    return _ret({"result": res, "step": f"{base}^{exponent} = {res}", "note": note})

# ---------- Expression helpers ----------
@mcp.tool()
def simplify_expression(expression: str) -> dict:
    """Algebraically simplify an expression (numbers, + - * / ^, parentheses)."""
    try:
        simp = sym_simplify(sympify(expression))
        return _ret({"simplified": str(simp)})
    except Exception as e:
        return _ret({"error": f"simplify failed: {e}"})

@mcp.tool()
def evaluate_expression(expression: str) -> dict:
    """Evaluate a numeric expression string into a float."""
    try:
        val = sympify(expression).evalf()
        if isinstance(val, SymFloat):
            return _ret({"value": float(val)})
        return _ret({"error": "expression did not evaluate to a numeric value"})
    except Exception as e:
        return _ret({"error": f"evaluate failed: {e}"})

@mcp.tool()
def check_answer(verifier_expression: str, final_answer: float, tolerance: float = 1e-9) -> dict:
    """
    Re-evaluate verifier_expression and compare to final_answer within tolerance.
    """
    try:
        expected = sympify(verifier_expression).evalf()
        if not isinstance(expected, SymFloat):
            return _ret({"ok": False, "error": "verifier did not reduce to a number"})
        expected_f = float(expected)
        ok = abs(expected_f - float(final_answer)) <= float(tolerance)
        return _ret({"ok": ok, "expected": expected_f, "final": float(final_answer)})
    except Exception as e:
        return _ret({"ok": False, "error": f"check failed: {e}"})

# ---------- Telegram ----------
@mcp.tool()
def send_telegram(message: str) -> dict:
    """
    Send a text message via Telegram Bot API.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return _ret({"sent": False, "error": "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"})

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=20)
    return _ret({"sent": resp.ok, "status": resp.status_code})

# ---------- Direct run helper (dev) ----------
if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
