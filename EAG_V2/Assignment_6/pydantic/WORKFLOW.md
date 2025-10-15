# Complete Agent Workflow

This document traces a complete execution through all 4 cognitive layers.

## 📋 Example Task

**Task:** "Calculate ASCII values of 'INDIA', sum their exponentials, then draw the result in a browser."

## 🎯 Phase 1: User Preference Collection

```
🎯 WELCOME TO THE COGNITIVE AGENT SYSTEM
=========================================================

🎨 What's your favorite color? purple
📍 Where are you located? California
🎯 What are your interests? mathematics, visualization
📊 Preferred math difficulty: 2 (medium)

✅ Preferences saved!
```

**Output:** `UserPreferences` Pydantic model
```python
UserPreferences(
    favorite_color="purple",
    location="California",
    interests=["mathematics", "visualization"],
    math_difficulty="medium"
)
```

---

## 🔄 Phase 2: Cognitive Loop - Iteration 1

### 🧠 Layer 1: PERCEPTION

**Input:** `PerceptionInput`
```python
PerceptionInput(
    query="Calculate ASCII values of 'INDIA'...",
    context=[],  # First iteration, no context
    user_preferences=UserPreferences(...),
    available_tools=[{
        'name': 'strings_to_chars_to_int',
        'description': 'Convert string to ASCII values',
        'params': ['text']
    }, ...],
    system_prompt=""  # Built internally
)
```

**LLM Processing:**
The perception layer builds a comprehensive prompt including:
- User preferences (favorite color: purple)
- Available tools
- Reasoning framework
- Output format specification

**LLM Response:**
```
REASONING_TYPE: ARITHMETIC
THOUGHT_PROCESS: I need to convert the string 'INDIA' to ASCII values. 
This requires the strings_to_chars_to_int tool which takes a string and 
returns a list of ASCII integer values. I expect to get 5 numbers 
corresponding to I, N, D, I, A.
VERIFICATION: Each character should map to its ASCII value: 
I=73, N=78, D=68, I=73, A=65. Will verify the result matches these.
ACTION: FUNCTION_CALL: strings_to_chars_to_int|INDIA
CONFIDENCE: 1.0
ERROR_CHECK: false
```

**Output:** `PerceptionOutput`
```python
PerceptionOutput(
    reasoning_type=ReasoningType.ARITHMETIC,
    thought_process="I need to convert the string 'INDIA' to ASCII values...",
    proposed_action="FUNCTION_CALL: strings_to_chars_to_int|INDIA",
    confidence=1.0,
    requires_verification=True,
    error_detected=False
)
```

---

### 💾 Layer 2: MEMORY

**Current State:**
```python
MemoryState(
    entries=[],  # Empty - first iteration
    current_iteration=0,
    intermediate_results={},
    final_answer=None
)
```

**Action:** Provides empty context to decision layer (first iteration)

---

### ⚖️ Layer 3: DECISION-MAKING

**Input:** `DecisionInput`
```python
DecisionInput(
    perception_output=PerceptionOutput(...),
    memory_state=MemoryState(...),
    max_iterations=15
)
```

**Decision Process:**
1. ✅ Check iteration limit (0/15 - OK)
2. ✅ Check action format (FUNCTION_CALL - OK)
3. ✅ Check for repeated actions (None - OK)
4. ✅ Evaluate safety (Confidence=1.0 - Safe)
5. ✅ Check verification need (Yes, but proceed)

**Output:** `DecisionOutput`
```python
DecisionOutput(
    decision_type=DecisionType.EXECUTE_TOOL,
    should_execute=True,
    action_to_execute="FUNCTION_CALL: strings_to_chars_to_int|INDIA",
    reasoning="Executing tool based on reasoning: convert INDIA to ASCII",
    continue_iteration=True,
    fallback_action=None
)
```

---

### ⚡ Layer 4: ACTION

**Input:** `ActionInput`
```python
ActionInput(
    decision=DecisionOutput(...),
    memory_state=MemoryState(...)
)
```

**Execution Process:**
1. Parse function call: `strings_to_chars_to_int` with params `["INDIA"]`
2. Get tool schema from MCP session
3. Match parameters: `{'text': 'INDIA'}`
4. Call MCP tool: `session.call_tool('strings_to_chars_to_int', {'text': 'INDIA'})`
5. Receive result: `[73, 78, 68, 73, 65]`

**Output:** `ActionOutput`
```python
ActionOutput(
    action_result=ActionResult(
        success=True,
        result=[73, 78, 68, 73, 65],
        error_message=None,
        tool_call=ToolCall(
            tool_name='strings_to_chars_to_int',
            arguments={'text': 'INDIA'}
        )
    ),
    updated_memory=MemoryState(
        entries=[
            MemoryEntry(
                iteration=1,
                function_name='strings_to_chars_to_int',
                arguments={'text': 'INDIA'},
                result=[73, 78, 68, 73, 65],
                reasoning="Convert INDIA to ASCII values",
                timestamp=1234567890.0
            )
        ],
        current_iteration=1,
        intermediate_results={'ascii_values': [73, 78, 68, 73, 65]},
        final_answer=None
    ),
    should_continue=True
)
```

**Memory Updated:** ✅

---

## 🔄 Phase 3: Cognitive Loop - Iteration 2

### 🧠 Layer 1: PERCEPTION

**Input:** `PerceptionInput`
```python
PerceptionInput(
    query="Calculate ASCII values of 'INDIA'...",
    context=[
        "Iteration 1: Called strings_to_chars_to_int({'text': 'INDIA'}) → [73, 78, 68, 73, 65]"
    ],  # Now has context!
    user_preferences=UserPreferences(...),
    available_tools=[...],
    system_prompt=""
)
```

**LLM Response:**
```
REASONING_TYPE: ARITHMETIC
THOUGHT_PROCESS: Previous iteration converted 'INDIA' to [73, 78, 68, 73, 65]. 
Now I need to calculate the sum of exponentials: e^73 + e^78 + e^68 + e^73 + e^65. 
This is a very large number. I'll use the int_list_to_exponential_sum tool.
VERIFICATION: The result should be a large floating point number. 
Will check if it's in expected range (e^78 dominates, so ~10^33).
ACTION: FUNCTION_CALL: int_list_to_exponential_sum|73,78,68,73,65
CONFIDENCE: 0.95
ERROR_CHECK: false
```

**Output:** `PerceptionOutput`
```python
PerceptionOutput(
    reasoning_type=ReasoningType.ARITHMETIC,
    thought_process="Previous iteration converted 'INDIA' to [73, 78, 68, 73, 65]...",
    proposed_action="FUNCTION_CALL: int_list_to_exponential_sum|73,78,68,73,65",
    confidence=0.95,
    requires_verification=True,
    error_detected=False
)
```

### 💾 💭 ⚖️ ⚡ (Decision → Action)

Similar flow, results in:
- Tool called: `int_list_to_exponential_sum`
- Result: `1.234567e+33`
- Memory updated with iteration 2

---

## 🔄 Phase 4: Cognitive Loop - Iteration 3-6 (Drawing)

### Iteration 3: Open Browser

**Perception Output:**
```
REASONING_TYPE: PLANNING
THOUGHT_PROCESS: Calculation complete. Result is 1.234567e+33. 
Now need to visualize in browser. First step: open browser with user's 
favorite color (purple).
ACTION: FUNCTION_CALL: open_browser|purple
```

**Action Result:** Browser opens with purple-themed HTML canvas

### Iteration 4: Draw Rectangle

**Perception Output:**
```
REASONING_TYPE: TOOL_USE
THOUGHT_PROCESS: Browser is open. Now draw rectangle for displaying result.
Using coordinates that create a large, visible rectangle.
ACTION: FUNCTION_CALL: draw_rectangle|100|100|600|400
```

**Action Result:** Purple rectangle drawn on canvas

### Iteration 5: Add Text

**Perception Output:**
```
REASONING_TYPE: TOOL_USE
THOUGHT_PROCESS: Rectangle drawn successfully. Now add the final answer 
text (1.234567e+33) inside the rectangle.
ACTION: FUNCTION_CALL: add_text_to_canvas|1.234567e+33
```

**Action Result:** Text "1.234567e+33" displayed in purple, centered

### Iteration 6: Final Answer

**Perception Output:**
```
REASONING_TYPE: FINAL_ANSWER
THOUGHT_PROCESS: All steps completed successfully:
1. ✅ Converted 'INDIA' to ASCII: [73, 78, 68, 73, 65]
2. ✅ Calculated exponential sum: 1.234567e+33
3. ✅ Opened browser with purple theme
4. ✅ Drew rectangle in purple
5. ✅ Added text to canvas
Task is complete.
VERIFICATION: All drawing steps verified successful. User can see result in browser.
ACTION: FINAL_ANSWER: 1.234567e+33
CONFIDENCE: 1.0
ERROR_CHECK: false
```

**Decision Output:**
```python
DecisionOutput(
    decision_type=DecisionType.PROVIDE_ANSWER,
    should_execute=True,
    action_to_execute="FINAL_ANSWER: 1.234567e+33",
    reasoning="Providing final answer, all steps complete",
    continue_iteration=False,  # Stop here!
    fallback_action=None
)
```

**Action Output:**
```python
ActionOutput(
    action_result=ActionResult(
        success=True,
        result="1.234567e+33",
        error_message=None,
        tool_call=None
    ),
    updated_memory=MemoryState(
        entries=[...6 entries...],
        current_iteration=6,
        intermediate_results={...},
        final_answer="1.234567e+33"  # Set!
    ),
    should_continue=False  # Loop ends!
)
```

---

## 🎯 Phase 5: Final Response

**Agent Response:**
```python
AgentResponse(
    success=True,
    final_answer="1.234567e+33",
    total_iterations=6,
    execution_summary=[
        "Step 1: strings_to_chars_to_int({'text': 'INDIA'}) → [73, 78, 68, 73, 65]",
        "Step 2: int_list_to_exponential_sum({'numbers': [73, 78, 68, 73, 65]}) → 1.234567e+33",
        "Step 3: open_browser({'favorite_color': 'purple'}) → Browser opened",
        "Step 4: draw_rectangle({'x1': 100, 'y1': 100, 'x2': 600, 'y2': 400}) → Rectangle drawn",
        "Step 5: add_text_to_canvas({'text': '1.234567e+33'}) → Text added",
        "Final Answer: 1.234567e+33"
    ],
    errors=[],
    user_preferences_used=UserPreferences(
        favorite_color="purple",
        location="California",
        interests=["mathematics", "visualization"],
        math_difficulty="medium"
    )
)
```

---

## 📊 Data Flow Diagram

```
User Input
    ↓
[UserPreferences] ──────────────────────────────────┐
    ↓                                               |
[Query String] ───────────────────┐                 |
    ↓                             |                 |
┌───────────────────────────────┐ |                 |
│   ITERATION LOOP (N times)    │ |                 |
│                               │ |                 |
│  ┌─────────────────────────┐ │ |                 |
│  │  PERCEPTION LAYER       │ │ |                 |
│  │  - Receives: Query,     │◄┼─┴─────────────────┤
│  │    Context, Prefs       │ │                   |
│  │  - Outputs:             │ │                   |
│  │    PerceptionOutput     │ │                   |
│  └──────────┬──────────────┘ │                   |
│             ↓                 │                   |
│  ┌─────────────────────────┐ │                   |
│  │  MEMORY LAYER           │ │                   |
│  │  - Provides: Context    │◄┼───────────────────┤
│  │  - Stores: History      │ │                   |
│  └──────────┬──────────────┘ │                   |
│             ↓                 │                   |
│  ┌─────────────────────────┐ │                   |
│  │  DECISION LAYER         │ │                   |
│  │  - Evaluates: Safety    │ │                   |
│  │  - Outputs:             │ │                   |
│  │    DecisionOutput       │ │                   |
│  └──────────┬──────────────┘ │                   |
│             ↓                 │                   |
│  ┌─────────────────────────┐ │                   |
│  │  ACTION LAYER           │ │                   |
│  │  - Executes: Tools      │ │                   |
│  │  - Updates: Memory      │ │                   |
│  │  - Outputs:             │ │                   |
│  │    ActionOutput         │ │                   |
│  └──────────┬──────────────┘ │                   |
│             ↓                 │                   |
│     Continue or Stop?         │                   |
│             ↓                 │                   |
└─────────────────────────────┘                   |
             ↓                                     |
    [AgentResponse] ◄──────────────────────────────┘
             ↓
      User sees result in browser
```

---

## 🎨 Visual Output

In the browser, the user sees:

```
╔════════════════════════════════════════════════════╗
║       🎨 AI Agent Drawing Canvas                   ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║    ┌────────────────────────────────────────┐     ║
║    │                                        │     ║
║    │                                        │     ║
║    │          1.234567e+33                  │     ║  <- Purple text
║    │                                        │     ║
║    │                                        │     ║
║    └────────────────────────────────────────┘     ║  <- Purple border
║                                                    ║
║  Status: Text added to canvas                     ║
║  Using your favorite color: purple                ║
╚════════════════════════════════════════════════════╝
```

---

## 🔍 Key Observations

### Pydantic Models Used
1. `UserPreferences` - Input
2. `PerceptionInput` - Layer 1 input
3. `PerceptionOutput` - Layer 1 output
4. `MemoryState` - Layer 2 state
5. `MemoryEntry` - Layer 2 entries
6. `DecisionInput` - Layer 3 input
7. `DecisionOutput` - Layer 3 output
8. `ActionInput` - Layer 4 input
9. `ActionOutput` - Layer 4 output
10. `ActionResult` - Layer 4 result
11. `ToolCall` - Tool execution
12. `AgentResponse` - Final output

**Total: 12 Pydantic models** - Every data structure is typed and validated!

### Cognitive Layer Benefits

1. **Perception** - Centralized reasoning, clear thought process
2. **Memory** - Context accumulation, no repeated work
3. **Decision** - Safety checks, verification, fallbacks
4. **Action** - Error handling, schema matching, execution

### User Preference Impact

- **Purple** used for all visual elements
- **California** could influence responses (not in this task)
- **Mathematics, visualization** interests acknowledged
- **Medium** difficulty appropriate for this task

---

## 🎓 This Workflow Demonstrates

✅ Complete cognitive architecture  
✅ Type-safe data flow  
✅ User personalization  
✅ Multi-turn conversation  
✅ Error resilience  
✅ Structured reasoning  
✅ Tool execution  
✅ Memory management  
✅ Decision validation  
✅ Visual output  

**Assignment 6: Complete Architecture Demonstration** 🎉

