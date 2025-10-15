"""
Perception Layer (LLM)
Responsible for understanding input, reasoning, and proposing actions
"""

import logging
from typing import List, Dict, Any
import google.generativeai as genai
import asyncio
from models import (
    PerceptionInput, 
    PerceptionOutput, 
    ReasoningType,
    UserPreferences
)

logger = logging.getLogger(__name__)


class PerceptionLayer:
    """
    Perception Layer uses LLM to understand queries and reason about solutions.
    This is the cognitive layer that interprets information and plans actions.
    """
    
    def __init__(self, llm_client: genai.GenerativeModel, timeout: int = 30):
        """
        Initialize the perception layer
        
        Args:
            llm_client: Configured Gemini LLM client
            timeout: Timeout for LLM calls in seconds
        """
        self.llm_client = llm_client
        self.timeout = timeout
        logger.info("Perception layer initialized")
    
    def _build_system_prompt(self, user_prefs: UserPreferences, available_tools: List[Dict[str, Any]]) -> str:
        """
        Build a comprehensive system prompt that passes all evaluation criteria
        
        ✅ Criteria covered:
        1. Explicit reasoning instructions
        2. Structured output format
        3. Separation of reasoning and tools
        4. Conversation loop support
        5. Instructional framing with examples
        6. Internal self-checks
        7. Reasoning type awareness
        8. Error handling and fallbacks
        9. Overall clarity
        """
        
        tools_description = "\n".join([
            f"  - {tool['name']}({', '.join(tool.get('params', []))}): {tool.get('description', 'No description')}"
            for tool in available_tools
        ])
        
        system_prompt = f"""You are an advanced reasoning agent with explicit step-by-step thinking capabilities. You help users solve mathematical problems and create visual representations in a web browser.

═══════════════════════════════════════════════════════════════════════
USER PREFERENCES (Apply these throughout your responses):
═══════════════════════════════════════════════════════════════════════
- Favorite Color: {user_prefs.favorite_color} (use this for visual elements)
- Language: {user_prefs.preferred_language}
- Location: {user_prefs.location or 'Not specified'}
- Interests: {', '.join(user_prefs.interests) if user_prefs.interests else 'General'}
- Math Difficulty: {user_prefs.math_difficulty}

═══════════════════════════════════════════════════════════════════════
REASONING FRAMEWORK
═══════════════════════════════════════════════════════════════════════

**STEP 1: UNDERSTAND & REASON (Before every action)**
Before taking any action, you MUST:
1. Clearly explain your understanding of the current situation
2. Identify what type of reasoning is needed (arithmetic/logic/tool_use/planning/verification)
3. Break down the problem into clear steps
4. Explain WHY the next action is necessary
5. Predict what the outcome should be

**STEP 2: TAG YOUR REASONING TYPE**
Every response must start with a reasoning type tag:
- [ARITHMETIC] - For mathematical calculations
- [LOGIC] - For logical deduction
- [TOOL_USE] - For using available tools
- [PLANNING] - For multi-step planning
- [VERIFICATION] - For checking previous results
- [FINAL_ANSWER] - For providing final response

**STEP 3: SELF-VERIFICATION**
After each action, you MUST:
- Verify the result makes sense
- Check if it matches your prediction
- Identify any errors or inconsistencies
- Decide if a correction is needed

═══════════════════════════════════════════════════════════════════════
AVAILABLE TOOLS
═══════════════════════════════════════════════════════════════════════
{tools_description}

═══════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (STRUCTURED & PARSEABLE)
═══════════════════════════════════════════════════════════════════════

Your response MUST follow this EXACT format:

REASONING_TYPE: [type]
THOUGHT_PROCESS: [Detailed step-by-step explanation of your thinking]
VERIFICATION: [What you expect to happen, how you'll verify correctness]
ACTION: [FUNCTION_CALL: tool_name|param1|param2 OR FINAL_ANSWER: result]
CONFIDENCE: [0.0-1.0]
ERROR_CHECK: [true/false - whether you detect any issues]

═══════════════════════════════════════════════════════════════════════
BROWSER DRAWING WORKFLOW (MUST FOLLOW THIS EXACT SEQUENCE)
═══════════════════════════════════════════════════════════════════════

When asked to draw or visualize:
1. [PLANNING] Plan: Calculate all results FIRST
2. [TOOL_USE] Call: open_browser (to open drawing website)
3. [TOOL_USE] Call: draw_rectangle|x1|y1|x2|y2 (use user's favorite color: {user_prefs.favorite_color})
4. [TOOL_USE] Call: add_text_to_canvas|text (write the answer)
5. [VERIFICATION] Verify: All drawing steps completed successfully
6. [FINAL_ANSWER] Provide: Final result

IMPORTANT: Use coordinates draw_rectangle|100|100|600|400 for a visible rectangle
IMPORTANT: Use the user's favorite color ({user_prefs.favorite_color}) for drawing

═══════════════════════════════════════════════════════════════════════
CONVERSATION LOOP & CONTEXT
═══════════════════════════════════════════════════════════════════════

You are operating in a multi-turn conversation where:
- Each iteration builds on previous results
- Context includes all previous function calls and results
- You must reference previous results by name
- Never repeat the same function call with identical parameters
- Update your reasoning based on new information

═══════════════════════════════════════════════════════════════════════
ERROR HANDLING & FALLBACKS
═══════════════════════════════════════════════════════════════════════

**If a tool fails:**
1. Acknowledge the failure explicitly
2. Analyze what went wrong
3. Propose a fallback action:
   - Try alternative tool
   - Retry with different parameters
   - Skip to next step if possible
   - Report limitation if no fallback exists

**If you're uncertain:**
1. State your uncertainty level explicitly
2. Explain what information is missing
3. Make your best inference with clear reasoning
4. Mark confidence level appropriately (<0.7)

**If result is unexpected:**
1. Flag it as [VERIFICATION] reasoning type
2. Explain why it's unexpected
3. Double-check the calculation/logic
4. Propose a correction if needed

═══════════════════════════════════════════════════════════════════════
EXAMPLES
═══════════════════════════════════════════════════════════════════════

Example 1 - Calculation:
REASONING_TYPE: ARITHMETIC
THOUGHT_PROCESS: Need to add 5 and 3. This is a simple arithmetic operation. I expect the result to be 8.
VERIFICATION: Will check if result equals 8. If not, will re-calculate.
ACTION: FUNCTION_CALL: add|5|3
CONFIDENCE: 1.0
ERROR_CHECK: false

Example 2 - After Receiving Result:
REASONING_TYPE: VERIFICATION
THOUGHT_PROCESS: Previous iteration returned 8 for add(5,3). This matches my expectation (5+3=8). The calculation is correct. Now I need to draw this result in the browser using the user's favorite color ({user_prefs.favorite_color}).
VERIFICATION: Next step is to open browser for drawing. I expect browser to open successfully.
ACTION: FUNCTION_CALL: open_browser
CONFIDENCE: 0.9
ERROR_CHECK: false

Example 3 - Error Handling:
REASONING_TYPE: LOGIC
THOUGHT_PROCESS: The browser_draw tool failed with "Connection timeout". This is an external failure. Fallback: I can still provide the answer without visualization.
VERIFICATION: Will provide final answer directly. User will receive correct result even without visual.
ACTION: FINAL_ANSWER: 8
CONFIDENCE: 0.8
ERROR_CHECK: true

Example 4 - Final Answer:
REASONING_TYPE: FINAL_ANSWER
THOUGHT_PROCESS: All steps completed successfully: (1) Calculated result=8, (2) Opened browser, (3) Drew rectangle in {user_prefs.favorite_color}, (4) Added text "8" to canvas. Task is complete.
VERIFICATION: All drawing steps verified successful. User can see the result in browser.
ACTION: FINAL_ANSWER: 8
CONFIDENCE: 1.0
ERROR_CHECK: false

═══════════════════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════════════════

1. ALWAYS explain your thinking before acting
2. ALWAYS tag your reasoning type
3. ALWAYS verify results make sense
4. ALWAYS handle errors gracefully with fallbacks
5. ALWAYS use structured output format
6. ALWAYS incorporate user preferences (especially {user_prefs.favorite_color} for visuals)
7. NEVER skip the reasoning explanation
8. NEVER give FINAL_ANSWER until all required steps are complete
9. NEVER repeat failed actions without modification

Your responses drive a structured agent loop. Clarity and consistency are critical.
"""
        return system_prompt
    
    async def _generate_with_timeout(self, prompt: str) -> str:
        """Generate LLM response with timeout"""
        logger.debug("Generating LLM response...")
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.llm_client.generate_content(prompt)
                ),
                timeout=self.timeout
            )
            logger.debug("LLM response generated successfully")
            return response.text.strip()
        except asyncio.TimeoutError:
            logger.error("LLM generation timed out")
            raise TimeoutError(f"LLM generation exceeded {self.timeout} seconds")
        except Exception as e:
            logger.error(f"Error in LLM generation: {e}")
            raise
    
    def _parse_llm_response(self, response_text: str) -> PerceptionOutput:
        """
        Parse structured LLM response into PerceptionOutput
        
        Args:
            response_text: Raw text from LLM
            
        Returns:
            Parsed PerceptionOutput
        """
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        
        # Initialize default values
        reasoning_type = ReasoningType.LOGIC
        thought_process = ""
        proposed_action = ""
        confidence = 0.8
        requires_verification = False
        error_detected = False
        
        # Parse structured output
        for line in lines:
            if line.startswith("REASONING_TYPE:"):
                type_str = line.split(":", 1)[1].strip().strip("[]").lower()
                # Map to ReasoningType enum
                type_mapping = {
                    "arithmetic": ReasoningType.ARITHMETIC,
                    "logic": ReasoningType.LOGIC,
                    "tool_use": ReasoningType.TOOL_USE,
                    "planning": ReasoningType.PLANNING,
                    "verification": ReasoningType.VERIFICATION,
                    "final_answer": ReasoningType.FINAL_ANSWER
                }
                reasoning_type = type_mapping.get(type_str, ReasoningType.LOGIC)
                
            elif line.startswith("THOUGHT_PROCESS:"):
                thought_process = line.split(":", 1)[1].strip()
                
            elif line.startswith("VERIFICATION:"):
                verification_text = line.split(":", 1)[1].strip()
                thought_process += f" | Verification: {verification_text}"
                requires_verification = True
                
            elif line.startswith("ACTION:"):
                action_text = line.split(":", 1)[1].strip()
                if action_text.startswith("FUNCTION_CALL:") or action_text.startswith("FINAL_ANSWER:"):
                    proposed_action = action_text
                else:
                    # Prepend if missing
                    if "FUNCTION_CALL" in action_text or "|" in action_text:
                        proposed_action = f"FUNCTION_CALL: {action_text}"
                    else:
                        proposed_action = f"FINAL_ANSWER: {action_text}"
                        
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                    confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
                except ValueError:
                    confidence = 0.8
                    
            elif line.startswith("ERROR_CHECK:"):
                error_str = line.split(":", 1)[1].strip().lower()
                error_detected = error_str == "true"
        
        # Fallback: find ACTION line if parsing failed
        if not proposed_action:
            for line in lines:
                if "FUNCTION_CALL:" in line or "FINAL_ANSWER:" in line:
                    if "FUNCTION_CALL:" in line:
                        proposed_action = "FUNCTION_CALL:" + line.split("FUNCTION_CALL:")[1].strip()
                    else:
                        proposed_action = "FINAL_ANSWER:" + line.split("FINAL_ANSWER:")[1].strip()
                    break
        
        # If still no action found, raise error
        if not proposed_action:
            raise ValueError(f"Could not parse action from LLM response: {response_text}")
        
        return PerceptionOutput(
            reasoning_type=reasoning_type,
            thought_process=thought_process or "No explicit reasoning provided",
            proposed_action=proposed_action,
            confidence=confidence,
            requires_verification=requires_verification,
            error_detected=error_detected
        )
    
    async def perceive(self, perception_input: PerceptionInput) -> PerceptionOutput:
        """
        Main perception function: understand input and propose action
        
        Args:
            perception_input: Structured input with query, context, preferences
            
        Returns:
            PerceptionOutput with reasoning and proposed action
        """
        logger.info("Perception layer processing input")
        
        # Build system prompt with user preferences
        system_prompt = self._build_system_prompt(
            perception_input.user_preferences,
            perception_input.available_tools
        )
        
        # Build context from previous iterations
        context_str = "\n".join(perception_input.context) if perception_input.context else "This is the first iteration."
        
        # Construct full prompt
        full_prompt = f"""{system_prompt}

═══════════════════════════════════════════════════════════════════════
CURRENT TASK
═══════════════════════════════════════════════════════════════════════
Query: {perception_input.query}

Previous Context:
{context_str}

Now provide your structured response following the OUTPUT FORMAT exactly.
"""
        
        # Generate response
        response_text = await self._generate_with_timeout(full_prompt)
        logger.debug(f"Raw LLM response: {response_text}")
        
        # Parse into structured output
        perception_output = self._parse_llm_response(response_text)
        logger.info(f"Perception output: {perception_output.reasoning_type} -> {perception_output.proposed_action}")
        
        return perception_output

