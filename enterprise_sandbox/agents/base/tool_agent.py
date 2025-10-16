"""
Tool Call Agent Base Class

This module provides the base class for tool-calling agents in EnterpriseArena.
"""

import logging
import json
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

from .agent import BaseAgent, AgentResult, AgentState, AgentMessage

logger = logging.getLogger(__name__)


class ToolCallAgent(BaseAgent):
    """
    Base class for tool-calling agents.
    
    This class provides common functionality for agents that can call tools
    and functions to interact with external systems.
    """
    
    def __init__(self, model: str, **kwargs):
        """
        Initialize the tool call agent.
        
        Args:
            model: LLM model to use for the agent
            **kwargs: Additional agent-specific parameters
        """
        super().__init__(model, **kwargs)
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions: Dict[str, Dict[str, Any]] = {}
        self.max_tool_calls = kwargs.get("max_tool_calls", 10)
        self.tool_call_timeout = kwargs.get("tool_call_timeout", 30)
        self.enable_tool_retry = kwargs.get("enable_tool_retry", True)
        self.max_tool_retries = kwargs.get("max_tool_retries", 3)
        
        # Tool call tracking
        self.tool_calls_made = 0
        self.tool_call_history: List[Dict[str, Any]] = []
        self.current_tool_call: Optional[Dict[str, Any]] = None
        
        logger.info(f"Initialized tool call agent with {len(self.tools)} tools")
    
    def register_tool(self, name: str, function: Callable, description: str = "", 
                     parameters: Dict[str, Any] = None):
        """
        Register a tool with the agent.
        
        Args:
            name: Tool name
            function: Tool function to call
            description: Tool description
            parameters: Tool parameter schema
        """
        self.tools[name] = function
        self.tool_descriptions[name] = {
            "description": description,
            "parameters": parameters or {},
            "function": function
        }
        
        logger.debug(f"Registered tool: {name}")
    
    def unregister_tool(self, name: str):
        """
        Unregister a tool from the agent.
        
        Args:
            name: Tool name to unregister
        """
        if name in self.tools:
            del self.tools[name]
            del self.tool_descriptions[name]
            logger.debug(f"Unregistered tool: {name}")
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_tool_description(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get description for a specific tool.
        
        Args:
            name: Tool name
            
        Returns:
            Tool description dictionary if found, None otherwise
        """
        return self.tool_descriptions.get(name)
    
    def get_tools_schema(self) -> Dict[str, Any]:
        """
        Get schema for all available tools.
        
        Returns:
            Dict containing tool schemas
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for name, description in self.tool_descriptions.items():
            schema["properties"][name] = {
                "type": "function",
                "description": description["description"],
                "parameters": description["parameters"]
            }
        
        return schema
    
    def parse_tool_call(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Parse a tool call from a message.
        
        Args:
            message: Message containing tool call
            
        Returns:
            Parsed tool call dictionary if found, None otherwise
        """
        try:
            # Look for JSON tool calls in the message
            if "```json" in message:
                # Extract JSON from code block
                start = message.find("```json") + 7
                end = message.find("```", start)
                if end != -1:
                    json_str = message[start:end].strip()
                    tool_call = json.loads(json_str)
                    return tool_call
            
            # Look for direct JSON
            if message.strip().startswith("{") and message.strip().endswith("}"):
                tool_call = json.loads(message.strip())
                return tool_call
            
            # Look for function call format
            if "function_call:" in message.lower():
                lines = message.split('\n')
                tool_call = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        tool_call[key.strip()] = value.strip()
                return tool_call
            
            return None
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse tool call JSON: {e}")
            return None
        except Exception as e:
            logger.warning(f"Failed to parse tool call: {e}")
            return None
    
    async def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call.
        
        Args:
            tool_call: Tool call dictionary
            
        Returns:
            Tool execution result
        """
        try:
            tool_name = tool_call.get("name") or tool_call.get("function")
            if not tool_name:
                raise ValueError("Tool name not specified in tool call")
            
            if tool_name not in self.tools:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # Extract parameters
            parameters = tool_call.get("parameters", {}) or tool_call.get("args", {})
            
            # Record tool call
            self.current_tool_call = {
                "name": tool_name,
                "parameters": parameters,
                "timestamp": datetime.now()
            }
            
            self.tool_calls_made += 1
            self.tool_call_history.append(self.current_tool_call.copy())
            
            logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")
            
            # Execute the tool
            tool_function = self.tools[tool_name]
            result = await self._execute_tool_with_retry(tool_function, parameters)
            
            # Update tool call with result
            self.current_tool_call["result"] = result
            self.current_tool_call["success"] = True
            
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "execution_time": 0.0  # Could be calculated if needed
            }
            
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg)
            
            if self.current_tool_call:
                self.current_tool_call["result"] = error_msg
                self.current_tool_call["success"] = False
            
            return {
                "success": False,
                "tool_name": tool_call.get("name", "unknown"),
                "error": error_msg,
                "execution_time": 0.0
            }
    
    async def _execute_tool_with_retry(self, tool_function: Callable, parameters: Dict[str, Any]) -> Any:
        """
        Execute a tool function with retry logic.
        
        Args:
            tool_function: Tool function to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        last_error = None
        
        for attempt in range(self.max_tool_retries + 1):
            try:
                if asyncio.iscoroutinefunction(tool_function):
                    result = await tool_function(**parameters)
                else:
                    result = tool_function(**parameters)
                
                return result
                
            except Exception as e:
                last_error = e
                if attempt < self.max_tool_retries and self.enable_tool_retry:
                    logger.warning(f"Tool execution attempt {attempt + 1} failed: {e}, retrying...")
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    break
        
        raise last_error
    
    def format_tool_result(self, result: Dict[str, Any]) -> str:
        """
        Format tool execution result for display.
        
        Args:
            result: Tool execution result
            
        Returns:
            Formatted result string
        """
        if result["success"]:
            return f"Tool '{result['tool_name']}' executed successfully. Result: {result['result']}"
        else:
            return f"Tool '{result['tool_name']}' failed: {result['error']}"
    
    def get_tool_call_summary(self) -> str:
        """
        Get a summary of tool calls made.
        
        Returns:
            str: Tool call summary
        """
        if not self.tool_call_history:
            return "No tool calls made."
        
        summary_parts = []
        for i, call in enumerate(self.tool_call_history):
            status = "✓" if call.get("success", False) else "✗"
            summary_parts.append(f"{i+1}. {status} {call['name']}")
        
        return "\n".join(summary_parts)
    
    def can_make_tool_call(self) -> bool:
        """
        Check if the agent can make another tool call.
        
        Returns:
            bool: True if can make another tool call, False otherwise
        """
        return self.tool_calls_made < self.max_tool_calls
    
    def get_tool_call_stats(self) -> Dict[str, Any]:
        """
        Get tool call statistics.
        
        Returns:
            Dict containing tool call statistics
        """
        successful_calls = sum(1 for call in self.tool_call_history if call.get("success", False))
        failed_calls = len(self.tool_call_history) - successful_calls
        
        return {
            "total_tool_calls": self.tool_calls_made,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / self.tool_calls_made if self.tool_calls_made > 0 else 0,
            "max_tool_calls": self.max_tool_calls,
            "remaining_calls": self.max_tool_calls - self.tool_calls_made,
            "available_tools": len(self.tools)
        }
    
    def reset_tool_calls(self):
        """Reset tool call tracking."""
        self.tool_calls_made = 0
        self.tool_call_history.clear()
        self.current_tool_call = None
        logger.debug("Tool call tracking reset")
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get the conversation messages for the agent.
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history
