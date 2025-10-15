"""
Main Agent Configuration
Integrates all 4 cognitive layers: Perception, Memory, Decision-Making, and Action
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import cognitive layers
from perception import PerceptionLayer
from memory import MemoryLayer
from decision_making import DecisionMakingLayer
from action import ActionLayer

# Import models
from models import (
    UserPreferences,
    PerceptionInput,
    DecisionInput,
    ActionInput,
    AgentConfig,
    AgentResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CognitiveAgent:
    """
    Cognitive Agent with 4 layers:
    1. Perception (LLM) - Understanding and reasoning
    2. Memory - Storing and retrieving information
    3. Decision-Making - Evaluating and deciding actions
    4. Action - Executing tools and interacting with environment
    """
    
    def __init__(self, 
                 llm_client: genai.GenerativeModel,
                 mcp_session: ClientSession,
                 user_preferences: UserPreferences,
                 config: AgentConfig):
        """
        Initialize the cognitive agent with all layers
        
        Args:
            llm_client: Configured LLM client
            mcp_session: Active MCP session
            user_preferences: User preferences for personalization
            config: Agent configuration
        """
        self.user_preferences = user_preferences
        self.config = config
        
        # Initialize all cognitive layers
        self.perception = PerceptionLayer(llm_client, timeout=config.llm_timeout)
        self.memory = MemoryLayer()
        self.decision_making = DecisionMakingLayer(
            enable_verification=config.enable_verification,
            enable_fallbacks=config.enable_fallbacks
        )
        self.action = ActionLayer(mcp_session)
        
        logger.info("Cognitive agent initialized with 4 layers")
        logger.info(f"User preferences: {user_preferences}")
    
    async def run(self, query: str) -> AgentResponse:
        """
        Main execution loop integrating all cognitive layers
        
        Args:
            query: The user's task or question
            
        Returns:
            AgentResponse with final result and execution summary
        """
        logger.info(f"Starting cognitive agent with query: {query}")
        
        errors = []
        
        # Get available tools
        tools_result = await self.action.mcp_session.list_tools()
        available_tools = []
        for tool in tools_result.tools:
            params = list(tool.inputSchema.get('properties', {}).keys())
            available_tools.append({
                'name': tool.name,
                'description': getattr(tool, 'description', ''),
                'params': params
            })
        
        logger.info(f"Available tools: {len(available_tools)}")
        
        # Main cognitive loop
        for iteration in range(self.config.max_iterations):
            logger.info(f"\n{'='*60}")
            logger.info(f"ITERATION {iteration + 1}/{self.config.max_iterations}")
            logger.info(f"{'='*60}")
            
            try:
                # LAYER 1: PERCEPTION - Understand and reason
                logger.info("🧠 PERCEPTION LAYER: Analyzing situation...")
                
                perception_input = PerceptionInput(
                    query=query,
                    context=self.memory.get_context_summary(),
                    user_preferences=self.user_preferences,
                    available_tools=available_tools,
                    system_prompt=""  # Built internally by perception layer
                )
                
                perception_output = await self.perception.perceive(perception_input)
                
                logger.info(f"   Reasoning Type: {perception_output.reasoning_type}")
                logger.info(f"   Thought: {perception_output.thought_process[:100]}...")
                logger.info(f"   Proposed Action: {perception_output.proposed_action}")
                logger.info(f"   Confidence: {perception_output.confidence}")
                
                # LAYER 2: MEMORY - Provide context (already used in perception)
                logger.info(f"💾 MEMORY LAYER: {len(self.memory.state.entries)} entries stored")
                
                # LAYER 3: DECISION MAKING - Evaluate and decide
                logger.info("⚖️  DECISION MAKING LAYER: Evaluating action...")
                
                decision_input = DecisionInput(
                    perception_output=perception_output,
                    memory_state=self.memory.get_state(),
                    max_iterations=self.config.max_iterations
                )
                
                decision_output = self.decision_making.decide(decision_input)
                
                logger.info(f"   Decision Type: {decision_output.decision_type}")
                logger.info(f"   Should Execute: {decision_output.should_execute}")
                logger.info(f"   Reasoning: {decision_output.reasoning[:100]}...")
                
                # Check if we should stop
                if not decision_output.should_execute:
                    logger.warning("Decision layer decided not to execute action")
                    errors.append(f"Iteration {iteration + 1}: Action blocked by decision layer")
                    break
                
                # LAYER 4: ACTION - Execute the decision
                logger.info("⚡ ACTION LAYER: Executing action...")
                
                action_input = ActionInput(
                    decision=decision_output,
                    memory_state=self.memory.get_state()
                )
                
                action_output = await self.action.execute(action_input)
                
                # Update memory with action results
                self.memory.state = action_output.updated_memory
                
                if action_output.action_result.success:
                    logger.info(f"   ✅ Action successful: {str(action_output.action_result.result)[:100]}")
                else:
                    logger.error(f"   ❌ Action failed: {action_output.action_result.error_message}")
                    errors.append(f"Iteration {iteration + 1}: {action_output.action_result.error_message}")
                
                # Check if we should continue
                if not action_output.should_continue:
                    logger.info("Agent decided to stop (task complete or error)")
                    break
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration + 1}: {e}")
                errors.append(f"Iteration {iteration + 1}: {str(e)}")
                import traceback
                traceback.print_exc()
                break
        
        # Prepare final response
        final_answer = self.memory.state.final_answer
        success = final_answer is not None and len(errors) == 0
        
        response = AgentResponse(
            success=success,
            final_answer=final_answer,
            total_iterations=self.memory.state.current_iteration,
            execution_summary=self.memory.get_execution_summary(),
            errors=errors,
            user_preferences_used=self.user_preferences
        )
        
        logger.info(f"\n{'='*60}")
        logger.info("AGENT EXECUTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Success: {success}")
        logger.info(f"Final Answer: {final_answer}")
        logger.info(f"Total Iterations: {response.total_iterations}")
        logger.info(f"Errors: {len(errors)}")
        
        return response


async def collect_user_preferences() -> UserPreferences:
    """
    Collect user preferences before starting the agent
    
    Returns:
        UserPreferences object
    """
    print("\n" + "="*60)
    print("🎯 WELCOME TO THE COGNITIVE AGENT SYSTEM")
    print("="*60)
    print("\nBefore we begin, let's learn about your preferences!")
    print("This will help personalize your experience.\n")
    
    # Collect preferences
    favorite_color = input("🎨 What's your favorite color? (for visualizations): ").strip() or "blue"
    location = input("📍 Where are you located? (optional): ").strip() or None
    
    print("\n🎯 What are your interests? (comma-separated)")
    interests_input = input("   (e.g., math, science, art): ").strip()
    interests = [i.strip() for i in interests_input.split(",")] if interests_input else []
    
    print("\n📊 Preferred math difficulty:")
    print("   1. Easy")
    print("   2. Medium")
    print("   3. Hard")
    difficulty_choice = input("   Choice (1-3): ").strip()
    difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
    difficulty = difficulty_map.get(difficulty_choice, "medium")
    
    preferences = UserPreferences(
        favorite_color=favorite_color,
        location=location,
        interests=interests,
        math_difficulty=difficulty
    )
    
    print("\n" + "="*60)
    print("✅ Preferences saved! Starting agent...")
    print("="*60 + "\n")
    
    return preferences


async def main():
    """Main entry point"""
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment")
        print("❌ Error: Please set GEMINI_API_KEY in .env file")
        return
    
    # Configure LLM
    genai.configure(api_key=api_key)
    llm_client = genai.GenerativeModel('gemini-2.0-flash')
    
    # Collect user preferences
    user_preferences = await collect_user_preferences()
    
    # Configure agent
    config = AgentConfig(
        max_iterations=15,
        llm_timeout=30,
        enable_verification=True,
        enable_fallbacks=True,
        log_level="INFO"
    )
    
    # Define the task
    print("\n📋 TASK:")
    task = """Calculate the ASCII values of characters in the word 'INDIA', 
then calculate the sum of exponentials of those values. 
After getting the final answer, open a browser with a drawing canvas, 
draw a rectangle, and write the final answer inside the rectangle."""
    print(task)
    print("\n")
    
    # Start MCP server and run agent
    logger.info("Connecting to MCP server...")
    
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_browser_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                logger.info("MCP session initialized")
                
                # Create and run agent
                agent = CognitiveAgent(
                    llm_client=llm_client,
                    mcp_session=session,
                    user_preferences=user_preferences,
                    config=config
                )
                
                response = await agent.run(task)
                
                # Display results
                print("\n" + "="*60)
                print("📊 FINAL RESULTS")
                print("="*60)
                print(f"\n✅ Success: {response.success}")
                print(f"🎯 Final Answer: {response.final_answer}")
                print(f"🔄 Total Iterations: {response.total_iterations}")
                
                if response.errors:
                    print(f"\n⚠️  Errors encountered: {len(response.errors)}")
                    for error in response.errors:
                        print(f"   - {error}")
                
                print("\n📝 Execution Summary:")
                for step in response.execution_summary:
                    print(f"   {step}")
                
                print("\n🎨 User Preferences Applied:")
                print(f"   - Favorite Color: {response.user_preferences_used.favorite_color}")
                print(f"   - Location: {response.user_preferences_used.location or 'Not specified'}")
                print(f"   - Interests: {', '.join(response.user_preferences_used.interests) or 'None'}")
                print(f"   - Difficulty: {response.user_preferences_used.math_difficulty}")
                
                print("\n" + "="*60)
                
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

