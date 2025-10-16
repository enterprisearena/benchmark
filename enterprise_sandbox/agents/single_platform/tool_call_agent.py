"""
Tool Call Agent Implementation

This module implements the tool-calling agent for single-platform tasks.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..base.agent import BaseAgent, AgentResult, AgentState, AgentType
from ..base.tool_agent import ToolCallAgent
from ..base.utils import AgentUtils

logger = logging.getLogger(__name__)


class SinglePlatformToolCallAgent(ToolCallAgent):
    """
    Tool-calling agent for single-platform tasks.
    
    This agent can call tools and functions to interact with enterprise platforms,
    making it suitable for complex operations that require multiple API calls.
    """
    
    def __init__(self, model: str, schema_obj: dict, **kwargs):
        """
        Initialize the tool-calling agent.
        
        Args:
            model: LLM model to use for the agent
            schema_obj: Platform schema object
            **kwargs: Additional agent-specific parameters
        """
        super().__init__(model, **kwargs)
        self.agent_type = AgentType.TOOL_CALL
        self.schema_obj = schema_obj
        self.schema = self._build_schema(schema_obj)
        
        # Tool-calling specific parameters
        self.max_tool_calls = kwargs.get("max_tool_calls", 15)
        self.tool_call_timeout = kwargs.get("tool_call_timeout", 30)
        self.enable_tool_retry = kwargs.get("enable_tool_retry", True)
        self.max_tool_retries = kwargs.get("max_tool_retries", 3)
        
        # Tool-calling state
        self.current_tool_call = None
        self.tool_call_results: List[Dict[str, Any]] = []
        self.execution_plan: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized tool-calling agent with {len(self.schema)} schema objects")
    
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
            schema_parts.append("Available Objects and Operations:")
            for obj_name, obj_info in schema_obj["objects"].items():
                schema_parts.append(f"  - {obj_name}: {obj_info.get('description', 'No description')}")
                
                # Add available operations
                operations = obj_info.get("operations", [])
                if operations:
                    schema_parts.append("    Available Operations:")
                    for operation in operations:
                        schema_parts.append(f"      - {operation}")
                
                # Add fields if available
                if "fields" in obj_info:
                    schema_parts.append("    Fields:")
                    for field_name, field_info in obj_info["fields"].items():
                        field_type = field_info.get("type", "unknown")
                        field_desc = field_info.get("description", "No description")
                        schema_parts.append(f"      - {field_name} ({field_type}): {field_desc}")
        
        # Add tool examples if available
        if "tool_examples" in schema_obj:
            schema_parts.append("\nTool Usage Examples:")
            for example in schema_obj["tool_examples"]:
                schema_parts.append(f"  - {example}")
        
        return "\n".join(schema_parts)
    
    def act(self, env, task_index: int) -> float:
        """
        Execute the tool-calling agent's action in the environment.
        
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
            
            # Start the tool-calling execution
            reward = self._execute_tool_calling_workflow(env, task)
            
            self.end_execution()
            return reward
            
        except Exception as e:
            return self.handle_error(e, "tool-calling execution").reward
    
    def _execute_tool_calling_workflow(self, env, task: Dict[str, Any]) -> float:
        """
        Execute the main tool-calling workflow.
        
        Args:
            env: Environment instance
            task: Task to execute
            
        Returns:
            float: Final reward
        """
        # Initialize environment
        observation, info = env.reset(task_index=task.get("idx", 0))
        self.add_system_message(f"Task: {task.get('task', 'No task description')}")
        self.add_system_message(f"Available tools: {', '.join(self.get_available_tools())}")
        
        total_reward = 0.0
        step_count = 0
        
        while not env.done and step_count < self.max_turns:
            try:
                # THINK: Analyze the current situation and plan tool calls
                thinking = self._think_about_tool_calls(observation, task, step_count)
                self.add_assistant_message(f"Thinking: {thinking}")
                
                # PLAN: Create execution plan
                execution_plan = self._create_execution_plan(thinking, observation, task)
                self.execution_plan = execution_plan
                
                # ACT: Execute tool calls
                tool_results = []
                for tool_call in execution_plan:
                    if not self.can_make_tool_call():
                        self.add_assistant_message("Maximum tool calls reached, stopping execution")
                        break
                    
                    tool_result = await self._execute_tool_call_step(tool_call, env)
                    tool_results.append(tool_result)
                    self.tool_call_results.append(tool_result)
                    
                    # Add tool result to conversation
                    self.add_assistant_message(f"Tool Call: {tool_call['name']}")
                    self.add_assistant_message(f"Result: {self.format_tool_result(tool_result)}")
                
                # OBSERVE: Process results and update environment
                observation, reward, done, info = env.step({
                    "action_type": "tool_calls",
                    "tool_results": tool_results,
                    "execution_plan": execution_plan
                })
                
                total_reward += reward
                step_count += 1
                self.increment_turn()
                
                # Check if task is complete
                if done:
                    logger.info(f"Task completed in {step_count} steps with reward {total_reward}")
                    break
                
            except Exception as e:
                logger.error(f"Error in tool-calling step {step_count}: {e}")
                self.add_assistant_message(f"Error: {str(e)}")
                break
        
        return total_reward
    
    def _think_about_tool_calls(self, observation: str, task: Dict[str, Any], step: int) -> str:
        """
        Think about what tool calls to make.
        
        Args:
            observation: Current observation from environment
            task: Task being executed
            step: Current step number
            
        Returns:
            str: Thinking text
        """
        # Build context for thinking
        context_parts = [
            f"Current step: {step}",
            f"Task: {task.get('task', 'No task description')}",
            f"Current observation: {observation}",
            f"Available tools: {', '.join(self.get_available_tools())}",
        ]
        
        if self.tool_call_results:
            context_parts.append("Previous tool call results:")
            for i, result in enumerate(self.tool_call_results[-3:]):  # Last 3 results
                context_parts.append(f"  {i+1}. {result.get('tool_name', 'unknown')}: {result.get('success', False)}")
        
        context = "\n".join(context_parts)
        
        # Generate thinking based on context
        thinking_parts = []
        
        # Analyze the task
        thinking_parts.append("Analyzing the task requirements:")
        task_text = task.get("task", "").lower()
        
        if "find" in task_text or "search" in task_text:
            thinking_parts.append("- Need to search for records")
            thinking_parts.append("- Should use query or search tools")
        elif "create" in task_text or "add" in task_text:
            thinking_parts.append("- Need to create new records")
            thinking_parts.append("- Should use create tools")
        elif "update" in task_text or "modify" in task_text:
            thinking_parts.append("- Need to update existing records")
            thinking_parts.append("- Should use update tools")
        
        # Plan tool sequence
        thinking_parts.append("\nPlanning tool call sequence:")
        thinking_parts.append("- Start with a query to understand the current state")
        thinking_parts.append("- Based on results, determine next actions")
        thinking_parts.append("- Use appropriate tools for the required operations")
        
        return "\n".join(thinking_parts)
    
    def _create_execution_plan(self, thinking: str, observation: str, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create execution plan for tool calls.
        
        Args:
            thinking: Current thinking
            observation: Current observation
            task: Task being executed
            
        Returns:
            List of tool call plans
        """
        execution_plan = []
        task_text = task.get("task", "").lower()
        
        # Determine tool calls based on task type
        if "find" in task_text or "search" in task_text:
            # Search/query tasks
            if "leads" in task_text:
                execution_plan.append({
                    "name": "search_leads",
                    "parameters": {
                        "criteria": self._extract_search_criteria(task_text),
                        "object_type": "Lead"
                    }
                })
            elif "accounts" in task_text:
                execution_plan.append({
                    "name": "search_accounts", 
                    "parameters": {
                        "criteria": self._extract_search_criteria(task_text),
                        "object_type": "Account"
                    }
                })
            elif "opportunities" in task_text:
                execution_plan.append({
                    "name": "search_opportunities",
                    "parameters": {
                        "criteria": self._extract_search_criteria(task_text),
                        "object_type": "Opportunity"
                    }
                })
            else:
                # Generic search
                execution_plan.append({
                    "name": "generic_search",
                    "parameters": {
                        "query": task_text,
                        "object_type": "Account"
                    }
                })
        
        elif "create" in task_text or "add" in task_text:
            # Create tasks
            if "lead" in task_text:
                execution_plan.append({
                    "name": "create_lead",
                    "parameters": {
                        "lead_data": self._extract_create_data(task_text, "lead")
                    }
                })
            elif "account" in task_text:
                execution_plan.append({
                    "name": "create_account",
                    "parameters": {
                        "account_data": self._extract_create_data(task_text, "account")
                    }
                })
            else:
                # Generic create
                execution_plan.append({
                    "name": "generic_create",
                    "parameters": {
                        "object_type": "Lead",
                        "data": self._extract_create_data(task_text)
                    }
                })
        
        elif "update" in task_text or "modify" in task_text:
            # Update tasks
            execution_plan.append({
                "name": "generic_update",
                "parameters": {
                    "object_type": "Lead",
                    "record_id": "placeholder_id",
                    "data": self._extract_update_data(task_text)
                }
            })
        
        else:
            # Default: start with a query
            execution_plan.append({
                "name": "generic_query",
                "parameters": {
                    "query": "SELECT Id, Name FROM Account LIMIT 10",
                    "object_type": "Account"
                }
            })
        
        return execution_plan
    
    def _extract_search_criteria(self, task_text: str) -> Dict[str, Any]:
        """Extract search criteria from task text."""
        criteria = {}
        
        # Look for specific criteria in the task text
        if "last" in task_text and "days" in task_text:
            # Extract number of days
            import re
            days_match = re.search(r'last[:\s]+(\d+)[:\s]+days?', task_text)
            if days_match:
                criteria["created_last_days"] = int(days_match.group(1))
        
        if "email" in task_text:
            # Look for email pattern
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', task_text)
            if email_match:
                criteria["Email"] = email_match.group(1)
        
        if "status" in task_text:
            # Look for status
            status_match = re.search(r'status[:\s]+([^\s]+)', task_text)
            if status_match:
                criteria["Status"] = status_match.group(1)
        
        return criteria
    
    def _extract_create_data(self, task_text: str, object_type: str = None) -> Dict[str, Any]:
        """Extract data for creating records from task text."""
        data = {}
        
        # Default data based on object type
        if object_type == "lead":
            data = {
                "FirstName": "John",
                "LastName": "Doe",
                "Email": "john.doe@example.com",
                "Company": "Example Corp"
            }
        elif object_type == "account":
            data = {
                "Name": "Example Account",
                "Type": "Customer"
            }
        else:
            data = {
                "Name": "Example Record"
            }
        
        return data
    
    def _extract_update_data(self, task_text: str) -> Dict[str, Any]:
        """Extract data for updating records from task text."""
        data = {}
        
        # Look for specific update fields
        if "status" in task_text:
            data["Status"] = "Updated"
        
        return data
    
    async def _execute_tool_call_step(self, tool_call: Dict[str, Any], env) -> Dict[str, Any]:
        """
        Execute a single tool call step.
        
        Args:
            tool_call: Tool call definition
            env: Environment instance
            
        Returns:
            Dict containing tool call result
        """
        try:
            tool_name = tool_call["name"]
            parameters = tool_call["parameters"]
            
            # Check if tool is registered
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "tool_name": tool_name,
                    "error": f"Tool '{tool_name}' not available"
                }
            
            # Execute the tool
            result = await self.execute_tool_call({
                "name": tool_name,
                "parameters": parameters
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Tool call execution failed: {e}")
            return {
                "success": False,
                "tool_name": tool_call.get("name", "unknown"),
                "error": str(e)
            }
    
    def get_execution_plan(self) -> List[Dict[str, Any]]:
        """
        Get the current execution plan.
        
        Returns:
            List of execution plan steps
        """
        return self.execution_plan.copy()
    
    def get_tool_call_results(self) -> List[Dict[str, Any]]:
        """
        Get the tool call results.
        
        Returns:
            List of tool call results
        """
        return self.tool_call_results.copy()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get the conversation messages for the agent.
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history
    
    def reset(self, args: Dict[str, Any]):
        """
        Reset the agent state for a new task.
        
        Args:
            args: Reset arguments
        """
        super().reset(args)
        self.current_tool_call = None
        self.tool_call_results.clear()
        self.execution_plan.clear()
        logger.debug("Tool-calling agent state reset")
