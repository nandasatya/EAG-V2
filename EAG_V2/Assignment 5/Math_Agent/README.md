# Math Agent with MCP Integration

An intelligent mathematical problem solver that uses Gemini AI with Model Context Protocol (MCP) to solve complex mathematical expressions step-by-step.

## Features

- **AI-Powered Math Solving**: Uses Gemini 2.0 Flash with function calling
- **MCP Server Integration**: Mathematical operations exposed as MCP tools
- **Step-by-Step Solutions**: Break down complex problems into atomic operations
- **Expression Evaluation**: Support for complex mathematical expressions using SymPy
- **Verification**: Built-in answer checking and validation
- **Telegram Integration**: Optional notification support

## Available Math Operations

1. `step_add(a, b)` - Addition
2. `step_subtract(a, b)` - Subtraction
3. `step_multiply(a, b)` - Multiplication
4. `step_divide(a, b)` - Division
5. `step_power(base, exponent)` - Exponentiation
6. `simplify_expression(expr)` - Simplify mathematical expressions
7. `evaluate_expression(expr)` - Evaluate complex expressions
8. `check_answer(verifier_expression, final_answer)` - Verify results
9. `send_telegram(message)` - Send results via Telegram (optional)

## Installation

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install google-genai mcp python-dotenv sympy requests
   ```

3. **Set up environment variables:**
   
   Create a `.env` file with:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token  # Optional
   TELEGRAM_CHAT_ID=your_chat_id               # Optional
   ```

   To get a Gemini API key:
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Create a new API key

## Usage

### Basic Usage

```bash
# Solve a mathematical expression (with uv)
uv run math_solver.py "5 + 7"

# Complex expression
uv run math_solver.py "((3/4) + (5/6)) * (7 - (2 + 9/3))^2"

# Use default problem
uv run math_solver.py
```

### Telegram Integration

The Math Agent automatically sends the problem and answer to your Telegram bot after solving:

```
Math Problem: 7 * 8
Answer: 56
```

To enable Telegram notifications, ensure your `.env` file contains:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

If Telegram is not configured, the agent will skip notifications gracefully.

### Example Output

```bash
$ python3 math_solver.py "2 + 3 * 4"
MCP tools: ['step_add', 'step_subtract', 'step_multiply', ...]
14
```

## Architecture

### Components

1. **math_solver.py** (Orchestrator)
   - Connects to Gemini AI
   - Manages MCP client connection
   - Handles function calling workflow
   - Returns final answers

2. **mcp_math_server.py** (MCP Server)
   - Exposes math operations as MCP tools
   - Uses SymPy for symbolic computation
   - Provides verification and validation
   - Optional Telegram integration

### How It Works

```
┌─────────────────┐
│  math_solver.py │  (Client)
│   Gemini AI     │
└────────┬────────┘
         │
         │ MCP Protocol
         │ (stdio)
         │
┌────────▼────────────┐
│ mcp_math_server.py  │  (Server)
│   Math Tools        │
│   SymPy Engine      │
└─────────────────────┘
```

## Optimization Tips

The agent is optimized to minimize API calls:

- **Use `evaluate_expression`** for most problems (1 call)
- Only uses step-by-step operations when needed
- Skips Telegram notifications by default
- **Typical usage: 3-5 API calls per problem**

### API Rate Limits

Gemini free tier allows **15 requests per minute**. If you hit the limit:
- Wait 60 seconds before retrying
- Consider upgrading to a paid tier for higher limits
- Use simpler expressions to reduce tool calls

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   - Ensure `.env` file exists with valid `GEMINI_API_KEY`
   - Check API key at [Google AI Studio](https://aistudio.google.com/apikey)

2. **Rate Limit Exceeded**
   - Wait 60 seconds between runs
   - Reduce problem complexity
   - Consider paid API tier

3. **Module Not Found**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **TypeError: object _AsyncGeneratorContextManager...**
   - This has been fixed - ensure you're using the latest version
   - Check that `connect_mcp()` uses `async with` properly

## Development

### Running Tests

```bash
# Test with simple expression
python3 math_solver.py "2 + 2"

# Test with complex expression
python3 math_solver.py "((3/4) + (5/6)) * (7 - (2 + 9/3))^2 + 15 / (3 * (2 + 1))"
```

### MCP Server Standalone

```bash
# Run MCP server directly (for debugging)
python3 mcp_math_server.py
```

## Requirements

- Python 3.11+
- google-genai
- mcp
- python-dotenv
- sympy
- requests (for Telegram integration)

## License

Part of EAG_V2 Assignment 5

## Credits

- Gemini AI by Google
- Model Context Protocol (MCP)
- SymPy for symbolic mathematics

