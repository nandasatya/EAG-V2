"""
Memory Layer
Responsible for storing and retrieving information about past actions
"""

import logging
import time
from typing import List, Dict, Any
from models import MemoryEntry, MemoryState

logger = logging.getLogger(__name__)


class MemoryLayer:
    """
    Memory Layer stores the history of actions, results, and reasoning.
    This provides the agent with context for decision-making.
    """
    
    def __init__(self):
        """Initialize the memory layer with empty state"""
        self.state = MemoryState()
        logger.info("Memory layer initialized")
    
    def store(self, 
              function_name: str, 
              arguments: Dict[str, Any], 
              result: Any, 
              reasoning: str) -> None:
        """
        Store a new memory entry
        
        Args:
            function_name: Name of the function that was called
            arguments: Arguments passed to the function
            result: Result returned by the function
            reasoning: Reasoning behind calling this function
        """
        entry = MemoryEntry(
            iteration=self.state.current_iteration + 1,
            function_name=function_name,
            arguments=arguments,
            result=result,
            reasoning=reasoning,
            timestamp=time.time()
        )
        
        self.state.add_entry(entry)
        logger.info(f"Stored memory entry: {function_name} at iteration {entry.iteration}")
        logger.debug(f"Memory entry details: args={arguments}, result={result}")
    
    def store_intermediate_result(self, key: str, value: Any) -> None:
        """
        Store an intermediate calculation result
        
        Args:
            key: Key to store the result under
            value: The intermediate result value
        """
        self.state.intermediate_results[key] = value
        logger.debug(f"Stored intermediate result: {key} = {value}")
    
    def get_intermediate_result(self, key: str) -> Any:
        """
        Retrieve an intermediate result
        
        Args:
            key: Key of the result to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        return self.state.intermediate_results.get(key)
    
    def set_final_answer(self, answer: Any) -> None:
        """
        Store the final answer
        
        Args:
            answer: The final answer value
        """
        self.state.final_answer = answer
        logger.info(f"Stored final answer: {answer}")
    
    def get_context_summary(self) -> List[str]:
        """
        Get a summary of all past actions for context
        
        Returns:
            List of strings describing past actions
        """
        summary = self.state.get_context_summary()
        logger.debug(f"Generated context summary with {len(summary)} entries")
        return summary
    
    def get_state(self) -> MemoryState:
        """
        Get the current memory state
        
        Returns:
            Current MemoryState object
        """
        return self.state
    
    def get_last_entry(self) -> MemoryEntry:
        """
        Get the most recent memory entry
        
        Returns:
            Last MemoryEntry, or None if no entries exist
        """
        if self.state.entries:
            return self.state.entries[-1]
        return None
    
    def has_called_function(self, function_name: str, arguments: Dict[str, Any] = None) -> bool:
        """
        Check if a function has already been called with given arguments
        
        Args:
            function_name: Name of the function to check
            arguments: Optional arguments to match. If None, only checks function name
            
        Returns:
            True if function has been called with those arguments
        """
        for entry in self.state.entries:
            if entry.function_name == function_name:
                if arguments is None:
                    return True
                elif entry.arguments == arguments:
                    return True
        return False
    
    def get_entries_by_function(self, function_name: str) -> List[MemoryEntry]:
        """
        Get all memory entries for a specific function
        
        Args:
            function_name: Name of the function
            
        Returns:
            List of MemoryEntry objects for that function
        """
        return [entry for entry in self.state.entries if entry.function_name == function_name]
    
    def clear(self) -> None:
        """Clear all memory (useful for starting fresh)"""
        self.state = MemoryState()
        logger.info("Memory cleared")
    
    def get_execution_summary(self) -> List[str]:
        """
        Get a human-readable summary of execution
        
        Returns:
            List of summary strings
        """
        summary = []
        summary.append(f"Total iterations: {self.state.current_iteration}")
        
        for entry in self.state.entries:
            result_str = str(entry.result)[:100]  # Truncate long results
            summary.append(
                f"Step {entry.iteration}: {entry.function_name}({entry.arguments}) → {result_str}"
            )
        
        if self.state.final_answer is not None:
            summary.append(f"Final Answer: {self.state.final_answer}")
        
        return summary
    
    def __repr__(self) -> str:
        """String representation of memory layer"""
        return f"MemoryLayer(entries={len(self.state.entries)}, iteration={self.state.current_iteration})"

