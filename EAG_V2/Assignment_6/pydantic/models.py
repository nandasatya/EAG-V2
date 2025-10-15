"""
Pydantic Models for Cognitive Agent
Defines all structured inputs and outputs for the agent system
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


# ==================== User Preferences ====================

class UserPreferences(BaseModel):
    """User preferences collected before agent execution"""
    favorite_color: str = Field(..., description="User's favorite color for visualizations")
    preferred_language: str = Field(default="English", description="User's preferred language")
    location: Optional[str] = Field(None, description="User's location")
    interests: List[str] = Field(default_factory=list, description="User's areas of interest")
    math_difficulty: Literal["easy", "medium", "hard"] = Field(default="medium", description="Preferred difficulty level")
    
    @field_validator('favorite_color')
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Ensure color is a valid string"""
        return v.strip().lower()


# ==================== Perception Layer ====================

class PerceptionInput(BaseModel):
    """Input to the perception layer (LLM)"""
    query: str = Field(..., description="The user's query or task")
    context: List[str] = Field(default_factory=list, description="Context from previous interactions")
    user_preferences: UserPreferences = Field(..., description="User preferences to personalize responses")
    available_tools: List[Dict[str, Any]] = Field(default_factory=list, description="Available tools for the agent")
    system_prompt: str = Field(..., description="System prompt for the LLM")


class ReasoningType(str, Enum):
    """Types of reasoning the agent can perform"""
    ARITHMETIC = "arithmetic"
    LOGIC = "logic"
    TOOL_USE = "tool_use"
    PLANNING = "planning"
    VERIFICATION = "verification"
    FINAL_ANSWER = "final_answer"


class PerceptionOutput(BaseModel):
    """Output from the perception layer"""
    reasoning_type: ReasoningType = Field(..., description="Type of reasoning being performed")
    thought_process: str = Field(..., description="Step-by-step reasoning explanation")
    proposed_action: str = Field(..., description="Proposed action in FUNCTION_CALL or FINAL_ANSWER format")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in the decision (0-1)")
    requires_verification: bool = Field(default=False, description="Whether this step needs verification")
    error_detected: bool = Field(default=False, description="Whether an error was detected")
    
    @field_validator('proposed_action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Ensure action starts with FUNCTION_CALL: or FINAL_ANSWER:"""
        if not (v.startswith("FUNCTION_CALL:") or v.startswith("FINAL_ANSWER:")):
            raise ValueError("Action must start with FUNCTION_CALL: or FINAL_ANSWER:")
        return v


# ==================== Memory Layer ====================

class MemoryEntry(BaseModel):
    """A single memory entry"""
    iteration: int = Field(..., description="Iteration number")
    function_name: str = Field(..., description="Function that was called")
    arguments: Dict[str, Any] = Field(..., description="Arguments passed to the function")
    result: Any = Field(..., description="Result from the function")
    reasoning: str = Field(..., description="Reasoning behind this action")
    timestamp: float = Field(..., description="Unix timestamp of the action")


class MemoryState(BaseModel):
    """Current state of the agent's memory"""
    entries: List[MemoryEntry] = Field(default_factory=list, description="List of memory entries")
    current_iteration: int = Field(default=0, description="Current iteration number")
    intermediate_results: Dict[str, Any] = Field(default_factory=dict, description="Intermediate calculation results")
    final_answer: Optional[Any] = Field(None, description="Final answer if computed")
    
    def add_entry(self, entry: MemoryEntry) -> None:
        """Add a new memory entry"""
        self.entries.append(entry)
        self.current_iteration += 1
    
    def get_context_summary(self) -> List[str]:
        """Get a summary of past actions for context"""
        return [
            f"Iteration {entry.iteration}: Called {entry.function_name}({entry.arguments}) → {entry.result}"
            for entry in self.entries
        ]


# ==================== Decision Making Layer ====================

class DecisionInput(BaseModel):
    """Input to the decision making layer"""
    perception_output: PerceptionOutput = Field(..., description="Output from perception layer")
    memory_state: MemoryState = Field(..., description="Current memory state")
    max_iterations: int = Field(default=10, description="Maximum allowed iterations")


class DecisionType(str, Enum):
    """Types of decisions the agent can make"""
    EXECUTE_TOOL = "execute_tool"
    PROVIDE_ANSWER = "provide_answer"
    REQUEST_VERIFICATION = "request_verification"
    HANDLE_ERROR = "handle_error"
    CONTINUE_REASONING = "continue_reasoning"


class DecisionOutput(BaseModel):
    """Output from the decision making layer"""
    decision_type: DecisionType = Field(..., description="Type of decision made")
    should_execute: bool = Field(..., description="Whether to execute the proposed action")
    action_to_execute: Optional[str] = Field(None, description="The action to execute if should_execute is True")
    reasoning: str = Field(..., description="Reasoning behind the decision")
    continue_iteration: bool = Field(default=True, description="Whether to continue to next iteration")
    fallback_action: Optional[str] = Field(None, description="Fallback action if primary action fails")


# ==================== Action Layer ====================

class ToolCall(BaseModel):
    """Structured tool call"""
    tool_name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(..., description="Arguments for the tool")


class ActionInput(BaseModel):
    """Input to the action layer"""
    decision: DecisionOutput = Field(..., description="Decision from decision layer")
    memory_state: MemoryState = Field(..., description="Current memory state")


class ActionResult(BaseModel):
    """Result of an action execution"""
    success: bool = Field(..., description="Whether the action succeeded")
    result: Any = Field(None, description="Result of the action")
    error_message: Optional[str] = Field(None, description="Error message if action failed")
    tool_call: Optional[ToolCall] = Field(None, description="The tool call that was executed")


class ActionOutput(BaseModel):
    """Output from the action layer"""
    action_result: ActionResult = Field(..., description="Result of the action")
    updated_memory: MemoryState = Field(..., description="Updated memory state after action")
    should_continue: bool = Field(..., description="Whether the agent should continue iterating")


# ==================== Agent Configuration ====================

class AgentConfig(BaseModel):
    """Configuration for the entire agent system"""
    max_iterations: int = Field(default=10, description="Maximum iterations before stopping")
    llm_timeout: int = Field(default=30, description="Timeout for LLM calls in seconds")
    enable_verification: bool = Field(default=True, description="Enable self-verification steps")
    enable_fallbacks: bool = Field(default=True, description="Enable fallback mechanisms")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")


# ==================== Final Response ====================

class AgentResponse(BaseModel):
    """Final response from the agent"""
    success: bool = Field(..., description="Whether the task was completed successfully")
    final_answer: Any = Field(None, description="The final answer")
    total_iterations: int = Field(..., description="Total number of iterations")
    execution_summary: List[str] = Field(..., description="Summary of execution steps")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    user_preferences_used: UserPreferences = Field(..., description="User preferences that were applied")

