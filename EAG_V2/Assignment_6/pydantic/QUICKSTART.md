# Quick Start Guide

Get up and running with the Cognitive Agent in 5 minutes!

## 🚀 Installation

```bash
# 1. Navigate to the project
cd /Users/satyananda/Desktop/code/EAG_V2/Assignment_6/pydantic

# 2. Install dependencies
pip install pydantic python-dotenv google-generativeai mcp

# 3. Set up environment
cp env_example.txt .env
nano .env  # Add your GEMINI_API_KEY
```

## 🔑 Get API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Add to `.env` file:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```

## ▶️ Run the Agent

```bash
python main.py
```

## 🎯 What You'll See

### Step 1: User Preferences
```
🎯 WELCOME TO THE COGNITIVE AGENT SYSTEM
=========================================================

🎨 What's your favorite color? (for visualizations): blue
📍 Where are you located? (optional): San Francisco
🎯 What are your interests? (comma-separated): math, AI
📊 Preferred math difficulty:
   1. Easy
   2. Medium
   3. Hard
   Choice (1-3): 2
```

### Step 2: Agent Execution
```
=========================================================
ITERATION 1/15
=========================================================
🧠 PERCEPTION LAYER: Analyzing situation...
   Reasoning Type: ARITHMETIC
   Thought: Converting INDIA to ASCII values...
   Proposed Action: FUNCTION_CALL: strings_to_chars_to_int|INDIA
   Confidence: 1.0

💾 MEMORY LAYER: 0 entries stored

⚖️  DECISION MAKING LAYER: Evaluating action...
   Decision Type: EXECUTE_TOOL
   Should Execute: True

⚡ ACTION LAYER: Executing action...
   ✅ Action successful: [73, 78, 68, 73, 65]
```

### Step 3: Browser Opens
A beautiful canvas opens in your browser with:
- Rectangle drawn in YOUR favorite color
- Final answer displayed in the center
- Clean, modern UI

### Step 4: Final Results
```
📊 FINAL RESULTS
=========================================================
✅ Success: True
🎯 Final Answer: 1.234567e+33
🔄 Total Iterations: 7

📝 Execution Summary:
   Step 1: strings_to_chars_to_int({'text': 'INDIA'}) → [73, 78, 68, 73, 65]
   Step 2: int_list_to_exponential_sum({'numbers': [73, 78, 68, 73, 65]}) → 1.234567e+33
   Step 3: open_browser({'favorite_color': 'blue'}) → Browser opened
   Step 4: draw_rectangle({'x1': 100, 'y1': 100, 'x2': 600, 'y2': 400}) → Rectangle drawn
   Step 5: add_text_to_canvas({'text': '1.234567e+33'}) → Text added
   Final Answer: 1.234567e+33

🎨 User Preferences Applied:
   - Favorite Color: blue
   - Location: San Francisco
   - Interests: math, AI
   - Difficulty: medium
```

## 🐛 Common Issues

### Issue: "GEMINI_API_KEY not found"
**Solution:** Make sure you created `.env` file and added your key.

### Issue: Browser doesn't open
**Solution:** Check `/tmp/agent_canvas_*.html` and open manually.

### Issue: "Module not found"
**Solution:** Install dependencies:
```bash
pip install pydantic python-dotenv google-generativeai mcp
```

## 📚 Next Steps

1. Read the full [README.md](README.md)
2. Review [PROMPT_EVALUATION.md](PROMPT_EVALUATION.md) to see how the prompt passes all 9 criteria
3. Explore the 4 cognitive layers:
   - `perception.py` - LLM reasoning
   - `memory.py` - Context storage
   - `decision_making.py` - Action evaluation
   - `action.py` - Tool execution

4. Try modifying the task in `main.py`:
   ```python
   task = """Your custom task here"""
   ```

## 🎨 Customization

### Change the Task
Edit `main.py`, line ~70:
```python
task = """Calculate factorial of 10, draw the result"""
```

### Adjust Iterations
Edit `main.py`, line ~60:
```python
config = AgentConfig(
    max_iterations=20,  # Increase if needed
    llm_timeout=30,
)
```

### Add New Tools
Edit `mcp_browser_server.py`:
```python
@mcp.tool()
def my_new_tool(param: str) -> str:
    """Description of what it does"""
    return result
```

## 🎉 Success!

You now have a fully functional cognitive agent with:
- ✅ 4 cognitive layers
- ✅ Pydantic models throughout
- ✅ Browser drawing capabilities
- ✅ User preference personalization
- ✅ Comprehensive reasoning system
- ✅ System prompt that passes all 9 evaluation criteria

**Happy experimenting! 🚀**

