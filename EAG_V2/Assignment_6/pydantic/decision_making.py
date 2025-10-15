"""
Decision Making Layer
Responsible for evaluating perception outputs and deciding what actions to take
"""

import logging
from models import (
    DecisionInput,
    DecisionOutput,
    DecisionType,
    PerceptionOutput,
    MemoryState,
    ReasoningType
)

logger = logging.getLogger(__name__)


class DecisionMakingLayer:
    """
    Decision Making Layer evaluates the perception layer's proposals
    and makes informed decisions about what to do next.
    """
    
    def __init__(self, enable_verification: bool = True, enable_fallbacks: bool = True):
        """
        Initialize the decision making layer
        
        Args:
            enable_verification: Whether to enable verification steps
            enable_fallbacks: Whether to enable fallback mechanisms
        """
        self.enable_verification = enable_verification
        self.enable_fallbacks = enable_fallbacks
        logger.info(f"Decision layer initialized (verification={enable_verification}, fallbacks={enable_fallbacks})")
    
    def _check_for_repeated_action(self, 
                                   perception: PerceptionOutput, 
                                   memory: MemoryState) -> bool:
        """
        Check if the proposed action has been executed before
        
        Args:
            perception: Current perception output
            memory: Current memory state
            
        Returns:
            True if action is a repeat
        """
        if not perception.proposed_action.startswith("FUNCTION_CALL:"):
            return False
        
        # Parse the function call
        try:
            _, call_info = perception.proposed_action.split(":", 1)
            parts = [p.strip() for p in call_info.split("|")]
            func_name = parts[0]
            
            # Check if we've called this function with same params
            for entry in memory.entries:
                if entry.function_name == func_name:
                    # Simple check: if function name is same, might be repeat
                    # More sophisticated: check arguments too
                    logger.warning(f"Potential repeated action detected: {func_name}")
                    return True
        except Exception as e:
            logger.debug(f"Could not parse function call for repeat check: {e}")
        
        return False
    
    def _should_request_verification(self, perception: PerceptionOutput) -> bool:
        """
        Determine if verification is needed
        
        Args:
            perception: Current perception output
            
        Returns:
            True if verification should be requested
        """
        if not self.enable_verification:
            return False
        
        # Request verification if:
        # 1. Perception explicitly requests it
        # 2. Confidence is low
        # 3. Error was detected
        if perception.requires_verification:
            return True
        if perception.confidence < 0.6:
            return True
        if perception.error_detected:
            return True
        
        return False
    
    def _generate_fallback_action(self, perception: PerceptionOutput) -> str:
        """
        Generate a fallback action if primary action might fail
        
        Args:
            perception: Current perception output
            
        Returns:
            Fallback action string
        """
        if not self.enable_fallbacks:
            return None
        
        # If error detected, try to continue without failing
        if perception.error_detected:
            return "FUNCTION_CALL: continue_with_best_effort"
        
        # If confidence is low, suggest verification
        if perception.confidence < 0.5:
            return "FUNCTION_CALL: request_user_clarification"
        
        return None
    
    def _check_iteration_limit(self, memory: MemoryState, max_iterations: int) -> bool:
        """
        Check if iteration limit has been reached
        
        Args:
            memory: Current memory state
            max_iterations: Maximum allowed iterations
            
        Returns:
            True if limit reached
        """
        if memory.current_iteration >= max_iterations:
            logger.warning(f"Iteration limit reached: {memory.current_iteration}/{max_iterations}")
            return True
        return False
    
    def _evaluate_action_safety(self, perception: PerceptionOutput, memory: MemoryState) -> tuple[bool, str]:
        """
        Evaluate if the proposed action is safe to execute
        
        Args:
            perception: Current perception output
            memory: Current memory state
            
        Returns:
            Tuple of (is_safe, reason)
        """
        # Check for repeated actions
        if self._check_for_repeated_action(perception, memory):
            # Allow repeats with different reasoning
            logger.info("Action appears to be repeated, but allowing with caution")
        
        # Check for error conditions
        if perception.error_detected:
            logger.warning("Error detected in perception output")
            return True, "Proceeding despite detected error (will use fallback if needed)"
        
        # Check confidence
        if perception.confidence < 0.3:
            return False, "Confidence too low to execute action safely"
        
        return True, "Action appears safe to execute"
    
    def decide(self, decision_input: DecisionInput) -> DecisionOutput:
        """
        Main decision function: evaluate perception and decide what to do
        
        Args:
            decision_input: Structured input with perception and memory
            
        Returns:
            DecisionOutput with the decision
        """
        perception = decision_input.perception_output
        memory = decision_input.memory_state
        max_iterations = decision_input.max_iterations
        
        logger.info(f"Decision layer evaluating action: {perception.proposed_action}")
        logger.debug(f"Reasoning type: {perception.reasoning_type}, Confidence: {perception.confidence}")
        
        # Check iteration limit
        if self._check_iteration_limit(memory, max_iterations):
            logger.warning("Max iterations reached, forcing completion")
            return DecisionOutput(
                decision_type=DecisionType.PROVIDE_ANSWER,
                should_execute=True,
                action_to_execute="FINAL_ANSWER: Maximum iterations reached",
                reasoning="Reached maximum iteration limit, providing best available answer",
                continue_iteration=False,
                fallback_action=None
            )
        
        # Handle FINAL_ANSWER
        if perception.proposed_action.startswith("FINAL_ANSWER:"):
            logger.info("Perception proposes final answer")
            return DecisionOutput(
                decision_type=DecisionType.PROVIDE_ANSWER,
                should_execute=True,
                action_to_execute=perception.proposed_action,
                reasoning=f"Providing final answer based on reasoning: {perception.thought_process}",
                continue_iteration=False,
                fallback_action=None
            )
        
        # Handle FUNCTION_CALL
        if perception.proposed_action.startswith("FUNCTION_CALL:"):
            # Evaluate safety
            is_safe, safety_reason = self._evaluate_action_safety(perception, memory)
            
            if not is_safe:
                logger.error(f"Action deemed unsafe: {safety_reason}")
                return DecisionOutput(
                    decision_type=DecisionType.HANDLE_ERROR,
                    should_execute=False,
                    action_to_execute=None,
                    reasoning=f"Cannot execute action: {safety_reason}",
                    continue_iteration=False,
                    fallback_action="FINAL_ANSWER: Unable to complete task safely"
                )
            
            # Check if verification needed
            if self._should_request_verification(perception):
                logger.info("Requesting verification for action")
                decision_type = DecisionType.REQUEST_VERIFICATION
                reasoning = f"Action requires verification (confidence={perception.confidence}): {safety_reason}"
            else:
                decision_type = DecisionType.EXECUTE_TOOL
                reasoning = f"Executing tool based on reasoning: {perception.thought_process}"
            
            # Generate fallback if needed
            fallback = self._generate_fallback_action(perception)
            
            return DecisionOutput(
                decision_type=decision_type,
                should_execute=True,
                action_to_execute=perception.proposed_action,
                reasoning=reasoning,
                continue_iteration=True,
                fallback_action=fallback
            )
        
        # Unknown action format
        logger.error(f"Unknown action format: {perception.proposed_action}")
        return DecisionOutput(
            decision_type=DecisionType.HANDLE_ERROR,
            should_execute=False,
            action_to_execute=None,
            reasoning=f"Cannot parse action format: {perception.proposed_action}",
            continue_iteration=False,
            fallback_action="FINAL_ANSWER: Error in action format"
        )
    
    def should_continue(self, decision: DecisionOutput, memory: MemoryState) -> bool:
        """
        Determine if the agent should continue iterating
        
        Args:
            decision: The decision that was made
            memory: Current memory state
            
        Returns:
            True if should continue
        """
        # Don't continue if:
        # 1. Decision says not to continue
        # 2. Final answer was provided
        # 3. Error with no fallback
        
        if not decision.continue_iteration:
            return False
        
        if decision.decision_type == DecisionType.PROVIDE_ANSWER:
            return False
        
        if decision.decision_type == DecisionType.HANDLE_ERROR and not decision.fallback_action:
            return False
        
        return True
    
    def __repr__(self) -> str:
        """String representation"""
        return f"DecisionMakingLayer(verification={self.enable_verification}, fallbacks={self.enable_fallbacks})"

