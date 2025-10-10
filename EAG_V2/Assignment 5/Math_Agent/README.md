# Math Agent with MCP Integration

An intelligent mathematical problem solver that uses Gemini AI with Model Context Protocol (MCP) to solve complex mathematical expressions with clear reasoning and verification.

## Features

- **AI-Powered Reasoning**: Uses Gemini 2.0 Flash with structured reasoning phases
- **MCP Server Integration**: Mathematical operations exposed as MCP tools
- **Transparent Problem Solving**: Shows reasoning before computation
- **Expression Evaluation**: Support for complex mathematical expressions using SymPy
- **Built-in Verification**: Automatic answer checking and validation
- **Self-Correction**: Detects and corrects errors in reasoning or computation
- **Telegram Integration**: Automatic notification of results

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
$ python3 math_solver.py "(3 + 5) * 2"

╭──────────────────────────╮
│ Math Problem Solver      │
╰──────────────────────────╯
╭──────────────────────────╮
│ Problem: (3 + 5) * 2     │
╰──────────────────────────╯

A: REASONING:
1. (Arithmetic) Identify operation inside parentheses: 3 + 5 = 8
2. (Arithmetic) Multiply result by 2 → expression = 8 * 2

FUNCTION_CALL: evaluate_expression|(3 + 5) * 2

FUNCTION CALL: evaluate_expression()
Expression: (3 + 5) * 2
Result: 16.0

A: FUNCTION_CALL: check_answer|(3 + 5) * 2|16

FUNCTION CALL: check_answer()
Verifying: (3 + 5) * 2 = 16.0
✓ Correct! (3 + 5) * 2 = 16.0

A: SELF_CHECK: Verified successfully.
FINAL_ANSWER: [16]

Final Answer: 16

FUNCTION CALL: send_telegram()
✓ Message sent via Telegram
Telegram: Message sent successfully

Calculation completed!
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
┌─────────────────────────────────────────────┐
│  math_solver.py (Client)                    │
│  ┌─────────────────────────────────────┐    │
│  │ Gemini AI with Structured Prompting │    │
│  │ • Reasoning Phase                   │    │
│  │ • Tool Phase                        │    │
│  │ • Verification Phase                │    │
│  │ • Self-Check Phase                  │    │
│  └─────────────────────────────────────┘    │
└──────────────────┬──────────────────────────┘
                   │
                   │ MCP Protocol (stdio)
                   │ JSON-RPC 2.0
                   │
┌──────────────────▼──────────────────────────┐
│  mcp_math_server.py (Server)                │
│  ┌─────────────────────────────────────┐    │
│  │ Math Tools                          │    │
│  │ • evaluate_expression (SymPy)       │    │
│  │ • check_answer (Verification)       │    │
│  │ • send_telegram (Notifications)     │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Problem Solving Workflow

The agent follows a **4-phase structured approach**:

1. **Reasoning Phase** 🤔
   - Analyzes the problem
   - Plans step-by-step approach
   - Labels reasoning types (Arithmetic, Logic, Simplification)

2. **Tool Phase** 🔧
   - Calls `evaluate_expression` to compute
   - Uses full or partial expressions as needed
   - Receives numerical results

3. **Verification Phase** ✓
   - Calls `check_answer` to verify correctness
   - Compares computed result with expected value
   - Detects discrepancies

4. **Self-Check & Finalization** 🎯
   - Reviews verification results
   - Corrects errors if found
   - Provides `FINAL_ANSWER` only when verified

## System Prompt Design

The Math Agent uses a **precise, structured system prompt** that enforces:

### Output Format Requirements

Every assistant response must contain **exactly one** of these:
- `REASONING:` - Numbered logical steps with labeled types
- `FUNCTION_CALL: function_name|param1|param2` - Tool invocation
- `FUNCTION_RESPONSE:` - Tool return value
- `SELF_CHECK:` - Validation or correction reasoning
- `FINAL_ANSWER: [answer]` - Confirmed final result

### Core Instructions

1. **Think before acting** - Write reasoning before calling tools
2. **Tool phase** - Use tools only after reasoning is complete
3. **Verification phase** - Always verify results with `check_answer`
4. **Error handling** - Self-correct if verification fails
5. **Final phase** - Provide answer only when verified

### Reasoning Labels

Each reasoning step is tagged with its type:
- **(Arithmetic)** - Basic calculations
- **(Logic)** - Logical deductions
- **(Simplification)** - Expression simplification
- **(Verification)** - Result checking

This structured approach ensures:
- ✓ Transparency in problem-solving
- ✓ Automatic verification
- ✓ Self-correction capabilities
- ✓ Minimal API calls (3-4 per problem)

## Performance

### API Call Efficiency

The agent is optimized to minimize API calls:

- **Typical workflow**: 3-4 function calls per problem
  1. Reasoning → `evaluate_expression`
  2. Result → `check_answer`
  3. Verified → `send_telegram`
  4. Final answer

- **API calls**: 2-3 LLM calls per problem
  1. Initial reasoning + first tool call
  2. Verification call
  3. Final answer (if needed)

### API Rate Limits

Gemini free tier allows **15 requests per minute**. If you hit the limit:
- Wait 60 seconds before retrying
- Consider upgrading to a paid tier for higher limits
- The current system is already optimized for minimal calls

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

## Key Improvements

### Structured Prompting Benefits

The updated system prompt provides several advantages over naive prompting:

1. **Clear Phase Separation** 
   - Forces reasoning before action
   - Prevents premature tool calling
   - Ensures verification is never skipped

2. **Format Enforcement**
   - Each response follows exact structure
   - Easier to parse and debug
   - Reduces parsing errors

3. **Self-Correction**
   - Built-in error detection
   - Automatic re-evaluation on failure
   - Never returns unverified answers

4. **Transparency**
   - Shows all reasoning steps
   - Labels types of reasoning used
   - Makes debugging easier

5. **Efficiency**
   - Minimizes redundant tool calls
   - Prevents infinite loops
   - Optimized for API rate limits

### Comparison: Before vs After

| Aspect | Before (Naive) | After (Structured) |
|--------|----------------|-------------------|
| **Tool Calls** | 8-15 per problem | 3-4 per problem |
| **API Calls** | 5-10+ per problem | 2-3 per problem |
| **Verification** | Sometimes skipped | Always enforced |
| **Self-Correction** | Manual | Automatic |
| **Reasoning** | Hidden | Explicit |
| **Error Rate** | Higher | Lower |

## Development

### Running Tests

```bash
# Test with simple expression
python3 math_solver.py "2 + 2"

# Test with complex expression
python3 math_solver.py "((3/4) + (5/6)) * (7 - (2 + 9/3))^2 + 15 / (3 * (2 + 1))"

# Test error handling (intentionally malformed)
python3 math_solver.py "5 / 0"
```

### MCP Server Standalone

```bash
# Run MCP server directly (for debugging)
python3 mcp_math_server.py
```

### Monitoring API Usage

Watch the console output to see:
- Number of function calls
- API call count
- Reasoning process
- Verification results

```bash
# The agent prints detailed logs to stderr
python3 math_solver.py "7 * 8" 2>&1 | grep "FUNCTION CALL"
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

## Prompt Engineering Principles

This Math Agent demonstrates key prompt engineering best practices:

### 1. Structured Output Format
- Forces consistent response structure
- Uses specific markers (`REASONING:`, `FUNCTION_CALL:`, etc.)
- Makes parsing reliable and deterministic

### 2. Phase-Based Workflow
- Separates thinking from acting
- Enforces verification before finalization
- Prevents premature conclusions

### 3. Self-Reflection
- Built-in `SELF_CHECK` phase
- Automatic error detection
- Re-evaluation on failure

### 4. Explicit Instructions
- Clear "must follow" requirements
- Concrete examples in prompt
- Error handling guidelines

### 5. Constraint Enforcement
- "Never skip verification"
- "Always reason before tool calls"
- "One response = one action"

### 6. Example-Driven Learning
- Complete workflow example in prompt
- Shows correct format
- Demonstrates expected behavior

### Result
These principles combine to create an agent that is:
- ✅ Reliable and consistent
- ✅ Transparent in reasoning
- ✅ Self-correcting
- ✅ Efficient with API calls
- ✅ Easy to debug and maintain

## Credits

- Gemini AI by Google
- Model Context Protocol (MCP)
- SymPy for symbolic mathematics
- Structured prompting techniques from modern prompt engineering

