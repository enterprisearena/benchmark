"""
ReAct Agent Implementation

This module implements the ReAct (Reasoning and Acting) agent for single-platform tasks.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..base.agent import BaseAgent, AgentResult, AgentState, AgentType
from ..base.chat_agent import ChatAgent
from ..base.utils import AgentUtils

logger = logging.getLogger(__name__)


class ReActAgent(ChatAgent):
    """
    ReAct (Reasoning and Acting) agent for single-platform tasks.
    
    This agent follows the ReAct pattern of reasoning about the current situation,
    taking an action, and observing the result before proceeding.
    """
    
    def __init__(self, model: str, schema_obj: dict, **kwargs):
        """
        Initialize the ReAct agent.
        
        Args:
            model: LLM model to use for the agent
            schema_obj: Platform schema object
            **kwargs: Additional agent-specific parameters
        """
        super().__init__(model, **kwargs)
        self.agent_type = AgentType.REACT
        self.schema_obj = schema_obj
        self.schema = self._build_schema(schema_obj)
        self.system_prompt = self._build_system_prompt(self.schema)
        
        # ReAct-specific parameters
        self.max_reasoning_steps = kwargs.get("max_reasoning_steps", 10)
        self.enable_self_correction = kwargs.get("enable_self_correction", True)
        self.reasoning_depth = kwargs.get("reasoning_depth", "detailed")
        
        # ReAct state
        self.current_reasoning = ""
        self.current_action = ""
        self.current_observation = ""
        self.reasoning_history: List[Dict[str, str]] = []
        
        logger.info(f"Initialized ReAct agent with {len(self.schema)} schema objects")
    
    def _build_schema(self, schema_obj: dict) -> str:
        """
        Build schema string from schema object.
        
        Args:
            schema_obj: Platform schema object
            
        Returns:
            str: Formatted schema string
        """
        if not schema_obj:
            return "No schema information available."
        
        schema_parts = []
        
        # Add object information
        if "objects" in schema_obj:
            schema_parts.append("Available Objects:")
            for obj_name, obj_info in schema_obj["objects"].items():
                schema_parts.append(f"  - {obj_name}: {obj_info.get('description', 'No description')}")
                
                # Add fields if available
                if "fields" in obj_info:
                    schema_parts.append("    Fields:")
                    for field_name, field_info in obj_info["fields"].items():
                        field_type = field_info.get("type", "unknown")
                        field_desc = field_info.get("description", "No description")
                        schema_parts.append(f"      - {field_name} ({field_type}): {field_desc}")
        
        # Add query examples if available
        if "query_examples" in schema_obj:
            schema_parts.append("\nQuery Examples:")
            for example in schema_obj["query_examples"]:
                schema_parts.append(f"  - {example}")
        
        # Add action examples if available
        if "action_examples" in schema_obj:
            schema_parts.append("\nAction Examples:")
            for example in schema_obj["action_examples"]:
                schema_parts.append(f"  - {example}")
        
        return "\n".join(schema_parts)
    
    def _build_system_prompt(self, schema: str) -> str:
        """
        Build system prompt for the ReAct agent.
        
        Args:
            schema: Platform schema string
            
        Returns:
            str: System prompt
        """
        base_prompt = """You are a ReAct (Reasoning and Acting) agent that helps users interact with enterprise software platforms.

Your task is to:
1. REASON about the user's request and the current situation
2. ACT by taking appropriate actions using the available tools
3. OBSERVE the results and continue reasoning

Available Schema Information:
{schema}

Instructions:
- Always follow the ReAct pattern: Thought -> Action -> Observation
- Be thorough in your reasoning before taking actions
- If an action fails, reason about why and try alternative approaches
- Provide clear explanations of your reasoning process
- Use the schema information to understand available objects and fields
- If you're unsure about something, ask for clarification

Response Format:
Thought: [Your reasoning about the current situation and what action to take]
Action: [The action you want to take, formatted as JSON if needed]
Observation: [What you observe from the action result]

Let's start!"""
        
        return base_prompt.format(schema=schema)
    
    def act(self, env, task_index: int) -> float:
        """
        Execute the ReAct agent's action in the environment.
        
        Args:
            env: Environment instance
            task_index: Index of the task to execute
            
        Returns:
            float: Reward received from the action
        """
        try:
            self.start_execution()
            self.set_state(AgentState.THINKING)
            
            # Get the task
            task = env.get_task(task_index)
            if not task:
                return self.handle_error(ValueError("Invalid task index"), "task retrieval").reward
            
            # Start the ReAct loop
            reward = self._execute_react_loop(env, task)
            
            self.end_execution()
            return reward
            
        except Exception as e:
            return self.handle_error(e, "ReAct execution").reward
    
    def _execute_react_loop(self, env, task: Dict[str, Any]) -> float:
        """
        Execute the main ReAct reasoning loop.
        
        Args:
            env: Environment instance
            task: Task to execute
            
        Returns:
            float: Final reward
        """
        # Initialize environment
        observation, info = env.reset(task_index=task.get("idx", 0))
        self.add_system_message(f"Task: {task.get('task', 'No task description')}")
        
        total_reward = 0.0
        step_count = 0
        
        while not env.done and step_count < self.max_turns:
            try:
                # REASON: Think about the current situation
                reasoning = self._reason_about_situation(observation, task, step_count)
                self.current_reasoning = reasoning
                self.add_assistant_message(f"Thought: {reasoning}")
                
                # ACT: Take an action based on reasoning
                action = self._determine_action(reasoning, observation, task)
                self.current_action = action
                
                # Execute action in environment
                observation, reward, done, info = env.step(action)
                total_reward += reward
                step_count += 1
                self.increment_turn()
                
                # OBSERVE: Process the observation
                observation_text = self._process_observation(observation, info)
                self.current_observation = observation_text
                self.add_assistant_message(f"Action: {action}")
                self.add_assistant_message(f"Observation: {observation_text}")
                
                # Record reasoning step
                self.reasoning_history.append({
                    "step": step_count,
                    "reasoning": reasoning,
                    "action": action,
                    "observation": observation_text,
                    "reward": reward
                })
                
                # Check if task is complete
                if done:
                    logger.info(f"Task completed in {step_count} steps with reward {total_reward}")
                    break
                
                # Self-correction if enabled
                if self.enable_self_correction and reward < 0:
                    correction = self._self_correct(reasoning, action, observation_text)
                    if correction:
                        self.add_assistant_message(f"Self-correction: {correction}")
                
            except Exception as e:
                logger.error(f"Error in ReAct step {step_count}: {e}")
                self.add_assistant_message(f"Error: {str(e)}")
                break
        
        return total_reward
    
    def _reason_about_situation(self, observation: str, task: Dict[str, Any], step: int) -> str:
        """
        Reason about the current situation and what action to take.
        
        Args:
            observation: Current observation from environment
            task: Task being executed
            step: Current step number
            
        Returns:
            str: Reasoning text
        """
        # Build context for reasoning
        context_parts = [
            f"Current step: {step}",
            f"Task: {task.get('task', 'No task description')}",
            f"Current observation: {observation}",
        ]
        
        if self.reasoning_history:
            context_parts.append("Previous steps:")
            for hist in self.reasoning_history[-3:]:  # Last 3 steps
                context_parts.append(f"  Step {hist['step']}: {hist['reasoning'][:100]}...")
        
        context = "\n".join(context_parts)
        
        # Generate reasoning based on context
        if self.reasoning_depth == "detailed":
            reasoning = self._generate_detailed_reasoning(context, task)
        else:
            reasoning = self._generate_simple_reasoning(context, task)
        
        return reasoning
    
    def _generate_detailed_reasoning(self, context: str, task: Dict[str, Any]) -> str:
        """
        Generate detailed reasoning about the situation.
        
        Args:
            context: Current context
            task: Task being executed
            
        Returns:
            str: Detailed reasoning
        """
        reasoning_parts = []
        
        # Analyze the current situation
        reasoning_parts.append("Analyzing the current situation:")
        reasoning_parts.append("- What information do I have?")
        reasoning_parts.append("- What is the user trying to accomplish?")
        reasoning_parts.append("- What actions are available to me?")
        
        # Consider the task requirements
        if "answer" in task:
            reasoning_parts.append(f"- The expected answer format is: {task['answer']}")
        
        if "reward_metric" in task:
            reasoning_parts.append(f"- Success will be measured by: {task['reward_metric']}")
        
        # Plan the next action
        reasoning_parts.append("\nPlanning my next action:")
        reasoning_parts.append("- Based on the schema, I can query objects and fields")
        reasoning_parts.append("- I should start with a broad query to understand the data")
        reasoning_parts.append("- Then refine my approach based on the results")
        
        return "\n".join(reasoning_parts)
    
    def _generate_simple_reasoning(self, context: str, task: Dict[str, Any]) -> str:
        """
        Generate simple reasoning about the situation.
        
        Args:
            context: Current context
            task: Task being executed
            
        Returns:
            str: Simple reasoning
        """
        return f"I need to {task.get('task', 'complete the task')}. Based on the current observation, I should take an appropriate action using the available schema."
    
    def _determine_action(self, reasoning: str, observation: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine the action to take based on reasoning.
        
        Args:
            reasoning: Current reasoning
            observation: Current observation
            task: Task being executed
            
        Returns:
            Dict: Action to take
        """
        # Parse the task to understand what action is needed
        task_text = task.get("task", "").lower()
        
        # Determine action type based on task content
        if "find" in task_text or "search" in task_text or "query" in task_text:
            return self._create_query_action(task)
        elif "create" in task_text or "add" in task_text:
            return self._create_create_action(task)
        elif "update" in task_text or "modify" in task_text:
            return self._create_update_action(task)
        elif "delete" in task_text or "remove" in task_text:
            return self._create_delete_action(task)
        else:
            # Default to query action
            return self._create_query_action(task)
    
    def _create_query_action(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a query action based on the task."""
        task_text = task.get("task", "")
        
        # Extract key information from task
        if "leads" in task_text.lower():
            return {
                "action_type": "query",
                "object_type": "Lead",
                "query": "SELECT Id, FirstName, LastName, Email, Company, Status FROM Lead",
                "filters": {}
            }
        elif "accounts" in task_text.lower():
            return {
                "action_type": "query", 
                "object_type": "Account",
                "query": "SELECT Id, Name, Type, Industry FROM Account",
                "filters": {}
            }
        elif "opportunities" in task_text.lower():
            return {
                "action_type": "query",
                "object_type": "Opportunity", 
                "query": "SELECT Id, Name, StageName, Amount, CloseDate FROM Opportunity",
                "filters": {}
            }
        else:
            return {
                "action_type": "query",
                "object_type": "Account",
                "query": "SELECT Id, Name FROM Account LIMIT 10",
                "filters": {}
            }
    
    def _create_create_action(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a create action based on the task."""
        return {
            "action_type": "create",
            "object_type": "Lead",
            "data": {
                "FirstName": "John",
                "LastName": "Doe", 
                "Email": "john.doe@example.com",
                "Company": "Example Corp"
            }
        }
    
    def _create_update_action(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create an update action based on the task."""
        return {
            "action_type": "update",
            "object_type": "Lead",
            "record_id": "00Q000000000000",
            "data": {
                "Status": "Qualified"
            }
        }
    
    def _create_delete_action(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a delete action based on the task."""
        return {
            "action_type": "delete",
            "object_type": "Lead",
            "record_id": "00Q000000000000"
        }
    
    def _process_observation(self, observation: str, info: Dict[str, Any]) -> str:
        """
        Process the observation from the environment.
        
        Args:
            observation: Raw observation
            info: Additional information
            
        Returns:
            str: Processed observation
        """
        if not observation:
            return "No observation received"
        
        # Add any additional context from info
        if info:
            context_parts = [observation]
            for key, value in info.items():
                if key != "observation":
                    context_parts.append(f"{key}: {value}")
            return " | ".join(context_parts)
        
        return observation
    
    def _self_correct(self, reasoning: str, action: Dict[str, Any], observation: str) -> Optional[str]:
        """
        Perform self-correction based on negative feedback.
        
        Args:
            reasoning: Previous reasoning
            action: Action that was taken
            observation: Result of the action
            
        Returns:
            str: Self-correction message if applicable, None otherwise
        """
        if "error" in observation.lower() or "failed" in observation.lower():
            return "I made an error in my previous action. Let me reconsider my approach and try a different strategy."
        
        return None
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get the conversation messages for the agent.
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history
    
    def get_reasoning_summary(self) -> str:
        """
        Get a summary of the reasoning process.
        
        Returns:
            str: Reasoning summary
        """
        if not self.reasoning_history:
            return "No reasoning steps recorded."
        
        summary_parts = []
        for step in self.reasoning_history:
            summary_parts.append(f"Step {step['step']}: {step['reasoning'][:100]}...")
        
        return "\n".join(summary_parts)
    
    def reset(self, args: Dict[str, Any]):
        """
        Reset the agent state for a new task.
        
        Args:
            args: Reset arguments
        """
        super().reset(args)
        self.current_reasoning = ""
        self.current_action = ""
        self.current_observation = ""
        self.reasoning_history.clear()
        logger.debug("ReAct agent state reset")
