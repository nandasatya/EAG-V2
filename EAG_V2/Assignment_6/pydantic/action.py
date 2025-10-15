"""
Action Layer
Responsible for executing tools and interacting with the environment
"""

import logging
import re
import time
from typing import Any, Dict
from mcp import ClientSession
from models import (
    ActionInput,
    ActionOutput,
    ActionResult,
    ToolCall,
    DecisionType,
    MemoryEntry
)
import time

logger = logging.getLogger(__name__)


class ActionLayer:
    """
    Action Layer executes tools and manages interactions with the environment.
    This is where the agent's decisions manifest as concrete actions.
    """
    
    def __init__(self, mcp_session: ClientSession):
        """
        Initialize the action layer
        
        Args:
            mcp_session: Active MCP session for tool execution
        """
        self.mcp_session = mcp_session
        logger.info("Action layer initialized")
    
    def _parse_function_call(self, action_string: str) -> ToolCall:
        """
        Parse a FUNCTION_CALL string into a ToolCall object
        
        Args:
            action_string: String in format "FUNCTION_CALL: tool_name|param1|param2"
            
        Returns:
            ToolCall object
        """
        if not action_string.startswith("FUNCTION_CALL:"):
            raise ValueError(f"Invalid function call format: {action_string}")
        
        # Remove "FUNCTION_CALL:" prefix
        call_info = action_string.split(":", 1)[1].strip()
        
        # Sometimes LLM adds extra labels like "TOOL_USE:" - remove them
        # Look for patterns like "TOOL_USE: function_name" or "REASONING_TYPE: function_name"
        for prefix in ["TOOL_USE:", "REASONING_TYPE:", "ACTION:"]:
            if call_info.startswith(prefix):
                call_info = call_info.split(":", 1)[1].strip()
                break
        
        # Split by pipe
        parts = [p.strip() for p in call_info.split("|")]
        
        if not parts:
            raise ValueError(f"No function name found in: {action_string}")
        
        tool_name = parts[0]
        params = parts[1:] if len(parts) > 1 else []
        
        logger.debug(f"Parsed function call: {tool_name} with {len(params)} parameters")
        
        return ToolCall(tool_name=tool_name, arguments={"params": params})
    
    def _match_parameters_to_schema(self, 
                                   tool_name: str, 
                                   params: list,
                                   tools_list: list) -> Dict[str, Any]:
        """
        Match parameters to tool schema
        
        Args:
            tool_name: Name of the tool
            params: List of parameter values
            tools_list: List of available tools with schemas
            
        Returns:
            Dictionary of parameter name -> value mappings
        """
        # Find the tool
        tool = next((t for t in tools_list if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Get schema
        schema = tool.inputSchema
        properties = schema.get('properties', {})
        
        logger.debug(f"Tool schema properties: {properties}")
        
        # Match parameters
        arguments = {}
        param_names = list(properties.keys())
        
        for i, param_value in enumerate(params):
            if i >= len(param_names):
                logger.warning(f"Extra parameter provided: {param_value}")
                break
            
            param_name = param_names[i]
            param_info = properties[param_name]
            param_type = param_info.get('type', 'string')
            
            # Convert to correct type
            try:
                if param_type == 'integer':
                    arguments[param_name] = int(param_value)
                elif param_type == 'number':
                    arguments[param_name] = float(param_value)
                elif param_type == 'boolean':
                    arguments[param_name] = param_value.lower() in ['true', '1', 'yes']
                elif param_type == 'array':
                    # Handle array input - can be in various formats:
                    # "[73, 78, 68]" or "73,78,68" or "{'numbers': [73, 78, 68]}"
                    if isinstance(param_value, str):
                        # Clean up common patterns
                        param_value = param_value.strip()
                        
                        # Handle dict-like format: "{'numbers': [73, 78, 68]}"
                        if '{' in param_value and ':' in param_value:
                            # Extract the array part
                            match = re.search(r'\[([^\]]+)\]', param_value)
                            if match:
                                param_value = match.group(1)
                        
                        # Remove brackets
                        param_value = param_value.strip('[]{}')
                        
                        # Remove quotes and split by comma
                        param_value = param_value.replace("'", "").replace('"', '')
                        values = [v.strip() for v in param_value.split(',')]
                        
                        # Convert to appropriate types (try int, then float, else string)
                        converted_values = []
                        for v in values:
                            # Skip empty values
                            if not v:
                                continue
                            # Skip key-value pairs like "numbers=..."
                            if '=' in v or ':' in v:
                                continue
                            try:
                                # Try integer first
                                converted_values.append(int(v))
                            except ValueError:
                                try:
                                    # Try float
                                    converted_values.append(float(v))
                                except ValueError:
                                    # Keep as string
                                    converted_values.append(v)
                        
                        arguments[param_name] = converted_values
                    else:
                        arguments[param_name] = param_value
                else:
                    arguments[param_name] = str(param_value)
            except Exception as e:
                logger.error(f"Error converting parameter {param_name}: {e}")
                arguments[param_name] = param_value
        
        logger.debug(f"Matched arguments: {arguments}")
        return arguments
    
    async def execute(self, action_input: ActionInput) -> ActionOutput:
        """
        Main execution function: execute the decided action
        
        Args:
            action_input: ActionInput with decision and memory state
            
        Returns:
            ActionOutput with results and updated memory
        """
        decision = action_input.decision
        memory_state = action_input.memory_state
        
        logger.info(f"Action layer executing: {decision.decision_type}")
        
        # Handle different decision types
        if decision.decision_type == DecisionType.PROVIDE_ANSWER:
            # Extract final answer
            if decision.action_to_execute and decision.action_to_execute.startswith("FINAL_ANSWER:"):
                answer = decision.action_to_execute.split(":", 1)[1].strip()
                memory_state.final_answer = answer
                
                result = ActionResult(
                    success=True,
                    result=answer,
                    error_message=None,
                    tool_call=None
                )
                
                logger.info(f"Final answer provided: {answer}")
                
                return ActionOutput(
                    action_result=result,
                    updated_memory=memory_state,
                    should_continue=False
                )
        
        elif decision.decision_type == DecisionType.EXECUTE_TOOL:
            # Execute the tool
            try:
                # Parse the function call
                tool_call = self._parse_function_call(decision.action_to_execute)
                
                # Get available tools
                tools_result = await self.mcp_session.list_tools()
                tools_list = tools_result.tools
                
                # Match parameters to schema
                params = tool_call.arguments.get("params", [])
                arguments = self._match_parameters_to_schema(
                    tool_call.tool_name,
                    params,
                    tools_list
                )
                
                logger.info(f"Calling tool: {tool_call.tool_name} with args: {arguments}")
                
                # Execute the tool
                result = await self.mcp_session.call_tool(tool_call.tool_name, arguments=arguments)
                
                # Extract result content
                if hasattr(result, 'content'):
                    if isinstance(result.content, list):
                        result_value = [
                            item.text if hasattr(item, 'text') else str(item)
                            for item in result.content
                        ]
                        if len(result_value) == 1:
                            result_value = result_value[0]
                    else:
                        result_value = str(result.content)
                else:
                    result_value = str(result)
                
                logger.info(f"Tool execution successful: {result_value}")
                
                # Store in memory
                memory_entry = MemoryEntry(
                    iteration=memory_state.current_iteration + 1,
                    function_name=tool_call.tool_name,
                    arguments=arguments,
                    result=result_value,
                    reasoning=decision.reasoning,
                    timestamp=time.time()
                )
                memory_state.entries.append(memory_entry)
                memory_state.current_iteration += 1
                
                action_result = ActionResult(
                    success=True,
                    result=result_value,
                    error_message=None,
                    tool_call=ToolCall(tool_name=tool_call.tool_name, arguments=arguments)
                )
                
                return ActionOutput(
                    action_result=action_result,
                    updated_memory=memory_state,
                    should_continue=decision.continue_iteration
                )
                
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                
                # Try fallback if available
                if decision.fallback_action:
                    logger.info(f"Attempting fallback: {decision.fallback_action}")
                    # For simplicity, return the error and let next iteration handle it
                
                action_result = ActionResult(
                    success=False,
                    result=None,
                    error_message=str(e),
                    tool_call=None
                )
                
                return ActionOutput(
                    action_result=action_result,
                    updated_memory=memory_state,
                    should_continue=False
                )
        
        elif decision.decision_type == DecisionType.HANDLE_ERROR:
            logger.error(f"Error handling decision: {decision.reasoning}")
            
            # Use fallback if available
            if decision.fallback_action:
                logger.info(f"Using fallback action: {decision.fallback_action}")
                # Could recursively call execute with fallback, but for simplicity:
                
                action_result = ActionResult(
                    success=False,
                    result=None,
                    error_message=decision.reasoning,
                    tool_call=None
                )
                
                return ActionOutput(
                    action_result=action_result,
                    updated_memory=memory_state,
                    should_continue=False
                )
        
        elif decision.decision_type == DecisionType.REQUEST_VERIFICATION:
            logger.info("Verification requested - continuing with execution")
            # For now, treat same as EXECUTE_TOOL but with logging
            # In a more sophisticated system, this would trigger a verification step
            
            # Change decision type to EXECUTE_TOOL and proceed
            if decision.action_to_execute and decision.action_to_execute.startswith("FUNCTION_CALL:"):
                # Parse and execute the tool directly (same logic as EXECUTE_TOOL)
                try:
                    tool_call = self._parse_function_call(decision.action_to_execute)
                    tools_result = await self.mcp_session.list_tools()
                    tools_list = tools_result.tools
                    params = tool_call.arguments.get("params", [])
                    arguments = self._match_parameters_to_schema(
                        tool_call.tool_name,
                        params,
                        tools_list
                    )
                    
                    logger.info(f"Calling tool (verification mode): {tool_call.tool_name} with args: {arguments}")
                    result = await self.mcp_session.call_tool(tool_call.tool_name, arguments=arguments)
                    
                    if hasattr(result, 'content'):
                        if isinstance(result.content, list):
                            result_value = [
                                item.text if hasattr(item, 'text') else str(item)
                                for item in result.content
                            ]
                            if len(result_value) == 1:
                                result_value = result_value[0]
                        else:
                            result_value = str(result.content)
                    else:
                        result_value = str(result)
                    
                    logger.info(f"Tool execution successful (verified): {result_value}")
                    
                    memory_entry = MemoryEntry(
                        iteration=memory_state.current_iteration + 1,
                        function_name=tool_call.tool_name,
                        arguments=arguments,
                        result=result_value,
                        reasoning=decision.reasoning + " [VERIFIED]",
                        timestamp=time.time()
                    )
                    memory_state.entries.append(memory_entry)
                    memory_state.current_iteration += 1
                    
                    action_result = ActionResult(
                        success=True,
                        result=result_value,
                        error_message=None,
                        tool_call=ToolCall(tool_name=tool_call.tool_name, arguments=arguments)
                    )
                    
                    return ActionOutput(
                        action_result=action_result,
                        updated_memory=memory_state,
                        should_continue=decision.continue_iteration
                    )
                    
                except Exception as e:
                    logger.error(f"Tool execution failed during verification: {e}")
                    action_result = ActionResult(
                        success=False,
                        result=None,
                        error_message=str(e),
                        tool_call=None
                    )
                    return ActionOutput(
                        action_result=action_result,
                        updated_memory=memory_state,
                        should_continue=False
                    )
        
        # Default fallback
        logger.warning(f"Unhandled decision type: {decision.decision_type}")
        action_result = ActionResult(
            success=False,
            result=None,
            error_message=f"Unhandled decision type: {decision.decision_type}",
            tool_call=None
        )
        
        return ActionOutput(
            action_result=action_result,
            updated_memory=memory_state,
            should_continue=False
        )
    
    def __repr__(self) -> str:
        """String representation"""
        return "ActionLayer(mcp_session=active)"

