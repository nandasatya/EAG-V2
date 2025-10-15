# System Prompt Evaluation

This document demonstrates how the system prompt in `perception.py` meets all 9 evaluation criteria.

## 📋 Evaluation Criteria Checklist

### 1. ✅ Explicit Reasoning Instructions

**Status:** ✅ PASS

**Evidence:**
```
STEP 1: UNDERSTAND & REASON (Before every action)
Before taking any action, you MUST:
1. Clearly explain your understanding of the current situation
2. Identify what type of reasoning is needed
3. Break down the problem into clear steps
4. Explain WHY the next action is necessary
5. Predict what the outcome should be
```

**Analysis:** The prompt explicitly requires the model to reason step-by-step before every action.

---

### 2. ✅ Structured Output Format

**Status:** ✅ PASS

**Evidence:**
```
Your response MUST follow this EXACT format:

REASONING_TYPE: [type]
THOUGHT_PROCESS: [Detailed step-by-step explanation]
VERIFICATION: [What you expect to happen]
ACTION: [FUNCTION_CALL: tool_name|param1|param2 OR FINAL_ANSWER: result]
CONFIDENCE: [0.0-1.0]
ERROR_CHECK: [true/false]
```

**Analysis:** Output format is predictable, parseable, and enforced with clear structure.

---

### 3. ✅ Separation of Reasoning and Tools

**Status:** ✅ PASS

**Evidence:**
- **REASONING_TYPE** tag separates thinking from action
- **THOUGHT_PROCESS** field for reasoning only
- **ACTION** field for tool calls only
- Clear distinction: "explain WHY" before "what to do"

**Workflow Example:**
1. REASONING_TYPE: ARITHMETIC (identifies reasoning)
2. THOUGHT_PROCESS: "Need to add 5+3..." (reasoning step)
3. ACTION: FUNCTION_CALL: add|5|3 (tool execution)

**Analysis:** Clear separation between cognitive reasoning and computational action.

---

### 4. ✅ Conversation Loop Support

**Status:** ✅ PASS

**Evidence:**
```
CONVERSATION LOOP & CONTEXT
You are operating in a multi-turn conversation where:
- Each iteration builds on previous results
- Context includes all previous function calls and results
- You must reference previous results by name
- Never repeat the same function call with identical parameters
- Update your reasoning based on new information
```

**Implementation:** The `PerceptionInput` model includes:
- `context: List[str]` - Previous iteration summaries
- Memory layer provides context automatically
- Examples show multi-turn reasoning

**Analysis:** Fully supports back-and-forth conversation with context accumulation.

---

### 5. ✅ Instructional Framing

**Status:** ✅ PASS

**Evidence:**
```
EXAMPLES

Example 1 - Calculation:
REASONING_TYPE: ARITHMETIC
THOUGHT_PROCESS: Need to add 5 and 3...
ACTION: FUNCTION_CALL: add|5|3
CONFIDENCE: 1.0

Example 2 - After Receiving Result:
REASONING_TYPE: VERIFICATION
THOUGHT_PROCESS: Previous iteration returned 8...
ACTION: FUNCTION_CALL: open_browser
```

Plus:
- BROWSER DRAWING WORKFLOW section with 6-step example
- Multiple format examples
- Clear "do this / don't do this" patterns

**Analysis:** Extensive examples and format specifications provided.

---

### 6. ✅ Internal Self-Checks

**Status:** ✅ PASS

**Evidence:**
```
STEP 3: SELF-VERIFICATION
After each action, you MUST:
- Verify the result makes sense
- Check if it matches your prediction
- Identify any errors or inconsistencies
- Decide if a correction is needed
```

Plus:
- **VERIFICATION** field in output format
- **ERROR_CHECK** field (true/false)
- Example 3 shows verification: "This matches my expectation (5+3=8)"

**Analysis:** Explicit self-verification instructions with structured output fields.

---

### 7. ✅ Reasoning Type Awareness

**Status:** ✅ PASS

**Evidence:**
```
STEP 2: TAG YOUR REASONING TYPE
Every response must start with a reasoning type tag:
- [ARITHMETIC] - For mathematical calculations
- [LOGIC] - For logical deduction
- [TOOL_USE] - For using available tools
- [PLANNING] - For multi-step planning
- [VERIFICATION] - For checking previous results
- [FINAL_ANSWER] - For providing final response
```

**Implementation:**
- `ReasoningType` enum in Pydantic models
- Required field in `PerceptionOutput`
- Examples demonstrate each type

**Analysis:** Complete reasoning type taxonomy with required tagging.

---

### 8. ✅ Error Handling and Fallbacks

**Status:** ✅ PASS

**Evidence:**
```
ERROR HANDLING & FALLBACKS

If a tool fails:
1. Acknowledge the failure explicitly
2. Analyze what went wrong
3. Propose a fallback action:
   - Try alternative tool
   - Retry with different parameters
   - Skip to next step if possible
   - Report limitation if no fallback exists

If you're uncertain:
1. State your uncertainty level explicitly
2. Explain what information is missing
3. Make your best inference with clear reasoning
4. Mark confidence level appropriately (<0.7)

If result is unexpected:
1. Flag it as [VERIFICATION] reasoning type
2. Explain why it's unexpected
3. Double-check the calculation/logic
4. Propose a correction if needed
```

**Implementation:**
- Decision-making layer handles fallbacks
- Example 3 shows error handling with fallback
- Confidence scores guide fallback decisions

**Analysis:** Comprehensive error handling with multiple fallback strategies.

---

### 9. ✅ Overall Clarity and Robustness

**Status:** ✅ EXCELLENT

**Strengths:**
- **Structure:** Clear sections with visual separators (═══)
- **Organization:** Logical flow from reasoning → format → tools → examples
- **Completeness:** Covers all aspects of agent behavior
- **User Integration:** Incorporates user preferences throughout
- **Consistency:** Uniform formatting and terminology
- **Actionability:** Every instruction is concrete and implementable

**Hallucination Prevention:**
- Structured output reduces free-form generation
- Examples anchor expected behavior
- Verification steps catch errors
- Confidence scoring flags uncertainty

**Analysis:** Highly clear, comprehensive, and robust prompt design.

---

## 📊 Final Evaluation

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
  "overall_clarity": "Excellent structure with comprehensive coverage of all 9 criteria. The prompt demonstrates professional-grade design with clear reasoning frameworks, robust error handling, and strong hallucination prevention through structured outputs."
}
```

### Score: 9/9 ✅

---

## 🎯 Key Innovations

### 1. Multi-Layer Integration
The prompt is not standalone - it's part of a 4-layer cognitive architecture:
- Perception (this prompt)
- Memory (provides context)
- Decision-Making (validates actions)
- Action (executes safely)

### 2. User Preference Integration
Unique feature: User preferences (favorite color, location, interests) are embedded directly in the prompt, personalizing all responses.

### 3. Pydantic Enforcement
The structured output format maps directly to Pydantic models, ensuring type safety and validation at the code level.

### 4. Browser Drawing Workflow
Specialized workflow for visual tasks with explicit step sequences and user-personalized colors.

---

## 🔬 Testing Recommendations

### Test Case 1: Simple Arithmetic
**Input:** "What is 25 + 75?"
**Expected:** 
- REASONING_TYPE: ARITHMETIC
- Clear thought process
- FUNCTION_CALL: add|25|75
- Verification that 25+75=100

### Test Case 2: Multi-Step with Drawing
**Input:** "Calculate factorial of 5, draw the result"
**Expected:**
- Multiple iterations with different REASONING_TYPE tags
- Memory reference in THOUGHT_PROCESS
- Browser drawing workflow followed
- Final answer in canvas

### Test Case 3: Error Handling
**Input:** "Divide 10 by 0"
**Expected:**
- Error detection
- Fallback strategy proposed
- Graceful degradation
- Final answer explaining limitation

### Test Case 4: Uncertainty
**Input:** "What is the square root of -1?"
**Expected:**
- Low confidence score (<0.7)
- Explicit uncertainty statement
- Best inference provided
- Error handling invoked

---

## 📈 Improvement Opportunities

While the prompt scores 9/9, here are potential enhancements:

1. **More Reasoning Types:** Add [RETRIEVAL], [SYNTHESIS], [COMPARISON]
2. **Confidence Calibration:** Add guidelines for setting confidence scores
3. **Example Diversity:** More examples of edge cases and errors
4. **Tool Chaining:** Explicit instructions for composing multiple tools
5. **User Clarification:** Protocol for asking user for missing information

---

## 🎓 Educational Value

This prompt demonstrates:
- **Best Practices** in prompt engineering
- **Structured Thinking** frameworks for LLMs
- **Error Resilience** through explicit handling
- **Multi-Turn Design** for agentic systems
- **Type Safety** integration with code
- **User Personalization** in AI systems

---

**Conclusion:** This system prompt represents a production-quality design suitable for real-world agentic AI systems, meeting all evaluation criteria with clear implementations and robust error handling.

