# Cognitive Agent with Pydantic Models

A sophisticated AI agent system implementing **4 cognitive layers**: Perception, Memory, Decision-Making, and Action. Built with structured Pydantic models throughout, featuring browser-based drawing and comprehensive reasoning capabilities.

## 🧠 Architecture Overview

### The 4 Cognitive Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY + PREFERENCES                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│  LAYER 1: PERCEPTION (LLM)                                   │
│  - Understands the task                                       │
│  - Reasons step-by-step                                       │
│  - Proposes actions with confidence scores                    │
│  - Tags reasoning type (arithmetic/logic/tool_use/etc.)       │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│  LAYER 2: MEMORY                                             │
│  - Stores all past actions and results                        │
│  - Provides context for decision-making                       │
│  - Tracks intermediate calculations                           │
│  - Maintains execution history                                │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│  LAYER 3: DECISION-MAKING                                    │
│  - Evaluates proposed actions                                 │
│  - Checks for repeated actions                                │
│  - Requests verification if needed                            │
│  - Generates fallback strategies                              │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│  LAYER 4: ACTION                                             │
│  - Executes tools via MCP                                     │
│  - Handles errors gracefully                                  │
│  - Updates memory with results                                │
│  - Manages browser drawing operations                         │
└─────────────────────┬────────────────────────────────────────┘
                      │
                 FINAL RESULT
```

## ✨ Key Features

### 🎯 User Preference Integration
Before the agent starts, it collects:
- **Favorite Color**: Used for all visual elements
- **Location**: For context-aware responses
- **Interests**: To personalize interactions
- **Math Difficulty**: Adjusts problem complexity

These preferences are embedded in the system prompt and influence all agent behavior.

### 📦 Structured with Pydantic
Every input and output uses Pydantic models:
- `UserPreferences` - User customization
- `PerceptionInput` / `PerceptionOutput` - LLM reasoning
- `MemoryState` / `MemoryEntry` - Historical context
- `DecisionInput` / `DecisionOutput` - Action evaluation
- `ActionInput` / `ActionOutput` - Tool execution
- `AgentResponse` - Final results

### 🌐 Browser Drawing (Not Paint!)
Instead of desktop Paint/PowerPoint, this version:
- Opens a beautiful HTML5 canvas in your browser
- Draws rectangles using your favorite color
- Adds text with dynamic styling
- Works cross-platform (macOS, Linux, Windows)

### 🧪 Comprehensive System Prompt
The prompt passes ALL 9 evaluation criteria:

1. ✅ **Explicit Reasoning Instructions** - Step-by-step thinking required
2. ✅ **Structured Output Format** - REASONING_TYPE, THOUGHT_PROCESS, ACTION format
3. ✅ **Separation of Reasoning and Tools** - Clear distinction between thinking and acting
4. ✅ **Conversation Loop Support** - Multi-turn context awareness
5. ✅ **Instructional Framing** - Multiple examples provided
6. ✅ **Internal Self-Checks** - VERIFICATION field in every response
7. ✅ **Reasoning Type Awareness** - Tags: [ARITHMETIC], [LOGIC], [TOOL_USE], etc.
8. ✅ **Error Handling & Fallbacks** - Explicit error handling instructions
9. ✅ **Overall Clarity** - Well-structured, comprehensive, unambiguous

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- Google Gemini API key

### Setup Steps

1. **Clone or navigate to the project:**
```bash
cd /Users/satyananda/Desktop/code/EAG_V2/Assignment_6/pydantic
```

2. **Install dependencies:**
```bash
pip install -e .
# or
pip install pydantic python-dotenv google-generativeai mcp asyncio
```

3. **Set up environment variables:**
```bash
cp env_example.txt .env
# Edit .env and add your GEMINI_API_KEY
```

4. **Get your Gemini API key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Create an API key
   - Add to `.env` file

## 🎮 Usage

### Basic Execution

```bash
python main.py
```

### What Happens

1. **Preference Collection**
   - You'll be asked about your favorite color, location, interests, etc.
   - These preferences personalize the entire experience

2. **Agent Execution**
   - The agent processes the task through all 4 cognitive layers
   - Each iteration shows:
     - 🧠 Perception: What the LLM is thinking
     - 💾 Memory: What's been stored
     - ⚖️ Decision: What decision was made
     - ⚡ Action: What action was executed

3. **Browser Drawing**
   - A beautiful HTML canvas opens in your browser
   - Rectangle drawn in your favorite color
   - Final answer displayed in the center

4. **Results**
   - Final answer displayed
   - Execution summary provided
   - User preferences confirmed

### Example Output

```
🎯 WELCOME TO THE COGNITIVE AGENT SYSTEM
=========================================================

🎨 What's your favorite color? (for visualizations): purple
📍 Where are you located? (optional): California
🎯 What are your interests? (comma-separated): math, AI, art

=========================================================
ITERATION 1/15
=========================================================
🧠 PERCEPTION LAYER: Analyzing situation...
   Reasoning Type: ARITHMETIC
   Thought: Need to convert 'INDIA' to ASCII values...
   Proposed Action: FUNCTION_CALL: strings_to_chars_to_int|INDIA
   Confidence: 1.0

⚖️  DECISION MAKING LAYER: Evaluating action...
   Decision Type: EXECUTE_TOOL
   Should Execute: True

⚡ ACTION LAYER: Executing action...
   ✅ Action successful: [73, 78, 68, 73, 65]

... (more iterations) ...

📊 FINAL RESULTS
=========================================================
✅ Success: True
🎯 Final Answer: 1.234567e+33
🔄 Total Iterations: 7
```

## 📁 Project Structure

```
pydantic/
├── main.py                    # Main agent orchestration
├── models.py                  # All Pydantic models
├── perception.py              # Perception layer (LLM)
├── memory.py                  # Memory layer
├── decision_making.py         # Decision-making layer
├── action.py                  # Action layer
├── mcp_browser_server.py      # MCP server with tools
├── pyproject.toml             # Project dependencies
├── env_example.txt            # Environment template
└── README.md                  # This file
```

## 🔧 Available Tools

### Mathematical Operations
- `add(a, b)` - Addition
- `subtract(a, b)` - Subtraction
- `multiply(a, b)` - Multiplication
- `divide(a, b)` - Division
- `power(a, b)` - Exponentiation
- `sqrt(a)` - Square root
- `factorial(a)` - Factorial
- `add_list(numbers)` - Sum of list
- `strings_to_chars_to_int(text)` - String to ASCII
- `int_list_to_exponential_sum(numbers)` - Sum of exponentials

### Browser Drawing
- `open_browser(favorite_color)` - Open canvas
- `draw_rectangle(x1, y1, x2, y2)` - Draw rectangle
- `add_text_to_canvas(text)` - Add text
- `clear_canvas()` - Clear drawing

## 🧪 Testing the Prompt Evaluation

The system prompt in `perception.py` is designed to pass all 9 criteria. To test it:

1. Extract the prompt from the code
2. Run it through the evaluation assistant
3. Verify all criteria are met

Example evaluation result:
```json
{
  "explicit_reasoning": true,
  "structured_output": true,
  "tool_separation": true,
  "conversation_loop": true,
  "instructional_framing": true,
  "internal_self_checks": true,
  "reasoning_type_awareness": true,
  "fallbacks": true,
  "overall_clarity": "Excellent structure with comprehensive coverage of all criteria"
}
```

## 🎯 Example Tasks

### Task 1: ASCII + Exponential Sum
```python
task = """Calculate ASCII values of 'INDIA', 
then sum of exponentials. Draw result in browser."""
```

### Task 2: Custom Math Problem
```python
task = """Calculate factorial of 10, 
divide by 720, draw the result."""
```

### Task 3: Multi-step Calculation
```python
task = """Add 25 and 75, multiply by 2, 
take square root, display in browser."""
```

## 🔍 Cognitive Layer Details

### Perception Layer (`perception.py`)
- Uses Gemini LLM for reasoning
- Builds comprehensive system prompt with user preferences
- Parses structured responses
- Handles timeouts gracefully

### Memory Layer (`memory.py`)
- Stores all function calls and results
- Provides context summaries
- Tracks intermediate results
- Enables execution replay

### Decision-Making Layer (`decision_making.py`)
- Evaluates action safety
- Checks for repeated actions
- Determines verification needs
- Generates fallback strategies

### Action Layer (`action.py`)
- Executes MCP tools
- Matches parameters to schemas
- Handles errors with fallbacks
- Updates memory automatically

## 🐛 Troubleshooting

### Browser doesn't open
- Check if you have a default browser set
- On macOS, Safari should open automatically
- Manual fallback: Open `/tmp/agent_canvas_*.html` directly

### LLM timeout errors
- Increase `llm_timeout` in `AgentConfig`
- Check your internet connection
- Verify API key is valid

### Tool execution errors
- Ensure MCP server is running
- Check parameter types match tool schema
- Review logs for detailed error messages

## 📚 Learning Resources

- **Pydantic Documentation**: https://docs.pydantic.dev/
- **MCP Protocol**: https://github.com/modelcontextprotocol
- **Google Gemini**: https://ai.google.dev/

## 🎓 Educational Value

This project demonstrates:
1. **Cognitive Architecture** - How to structure an AI agent
2. **Type Safety** - Using Pydantic for validation
3. **Separation of Concerns** - 4 distinct layers
4. **Error Handling** - Graceful degradation
5. **User Personalization** - Preference integration
6. **Structured Prompting** - High-quality LLM instructions

## 🤝 Contributing

This is an educational project for EAG_V2 Assignment 6. Feel free to:
- Experiment with different tasks
- Add new cognitive layers
- Enhance the prompt evaluation
- Improve browser drawing capabilities

## 📝 License

Educational project - MIT License

## 👨‍💻 Author

Created for EAG_V2 Assignment 6 - Cognitive Architecture with Pydantic

---

**Happy Coding! 🚀**

