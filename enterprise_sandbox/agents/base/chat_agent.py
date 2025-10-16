"""
Chat Agent Base Class

This module provides the base class for chat-based agents in EnterpriseArena.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .agent import BaseAgent, AgentResult, AgentState, AgentMessage

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """
    Base class for chat-based agents.
    
    This class provides common functionality for agents that interact through
    chat-based conversations with the environment.
    """
    
    def __init__(self, model: str, **kwargs):
        """
        Initialize the chat agent.
        
        Args:
            model: LLM model to use for the agent
            **kwargs: Additional agent-specific parameters
        """
        super().__init__(model, **kwargs)
        self.user_model = kwargs.get("user_model", "gpt-4o-2024-08-06")
        self.user_provider = kwargs.get("user_provider", "openai")
        self.max_message_length = kwargs.get("max_message_length", 4000)
        self.enable_memory = kwargs.get("enable_memory", True)
        self.memory_window = kwargs.get("memory_window", 10)  # Number of messages to keep in memory
        
        # Chat-specific state
        self.current_query = ""
        self.current_response = ""
        self.conversation_active = False
        
        logger.info(f"Initialized chat agent with user model {self.user_model}")
    
    def start_conversation(self, initial_query: str):
        """
        Start a new conversation.
        
        Args:
            initial_query: Initial query from the user
        """
        self.current_query = initial_query
        self.conversation_active = True
        self.set_state(AgentState.THINKING)
        
        # Add initial user message
        self.add_message("user", initial_query)
        
        logger.info(f"Started conversation with query: {initial_query[:100]}...")
    
    def end_conversation(self):
        """End the current conversation."""
        self.conversation_active = False
        self.current_query = ""
        self.current_response = ""
        self.set_state(AgentState.COMPLETED)
        
        logger.info("Conversation ended")
    
    def add_user_message(self, content: str):
        """
        Add a user message to the conversation.
        
        Args:
            content: User message content
        """
        self.add_message("user", content)
        self.current_query = content
        logger.debug(f"Added user message: {content[:50]}...")
    
    def add_assistant_message(self, content: str):
        """
        Add an assistant message to the conversation.
        
        Args:
            content: Assistant message content
        """
        self.add_message("assistant", content)
        self.current_response = content
        logger.debug(f"Added assistant message: {content[:50]}...")
    
    def add_system_message(self, content: str):
        """
        Add a system message to the conversation.
        
        Args:
            content: System message content
        """
        self.add_message("system", content)
        logger.debug(f"Added system message: {content[:50]}...")
    
    def get_conversation_context(self) -> List[Dict[str, str]]:
        """
        Get conversation context for the LLM.
        
        Returns:
            List of message dictionaries for LLM context
        """
        if not self.enable_memory:
            # Return only the last message
            if self.messages:
                return [self.messages[-1].__dict__]
            return []
        
        # Return messages within the memory window
        start_index = max(0, len(self.messages) - self.memory_window)
        context_messages = self.messages[start_index:]
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in context_messages
        ]
    
    def truncate_message(self, content: str) -> str:
        """
        Truncate message content if it exceeds maximum length.
        
        Args:
            content: Message content to truncate
            
        Returns:
            str: Truncated message content
        """
        if len(content) <= self.max_message_length:
            return content
        
        truncated = content[:self.max_message_length - 3] + "..."
        logger.warning(f"Message truncated from {len(content)} to {len(truncated)} characters")
        return truncated
    
    def format_conversation_for_llm(self) -> str:
        """
        Format conversation for LLM input.
        
        Returns:
            str: Formatted conversation string
        """
        context_messages = self.get_conversation_context()
        
        if not context_messages:
            return ""
        
        formatted_parts = []
        for msg in context_messages:
            role = msg["role"].upper()
            content = self.truncate_message(msg["content"])
            formatted_parts.append(f"{role}: {content}")
        
        return "\n\n".join(formatted_parts)
    
    def extract_response_from_llm(self, llm_response: str) -> str:
        """
        Extract the actual response from LLM output.
        
        Args:
            llm_response: Raw LLM response
            
        Returns:
            str: Extracted response content
        """
        # Remove any role prefixes that might be in the response
        lines = llm_response.strip().split('\n')
        
        # Look for the actual response content
        response_lines = []
        in_response = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts a response
            if line.upper().startswith(('ASSISTANT:', 'AI:', 'RESPONSE:')):
                in_response = True
                # Remove the prefix and add the content
                content = line.split(':', 1)[1].strip()
                if content:
                    response_lines.append(content)
            elif in_response:
                response_lines.append(line)
            elif not any(line.upper().startswith(prefix) for prefix in ['USER:', 'SYSTEM:', 'HUMAN:']):
                # If no role prefix, assume it's the response
                response_lines.append(line)
        
        response = '\n'.join(response_lines).strip()
        
        # If no response was extracted, use the original
        if not response:
            response = llm_response.strip()
        
        return response
    
    def validate_response(self, response: str) -> bool:
        """
        Validate the agent's response.
        
        Args:
            response: Response to validate
            
        Returns:
            bool: True if response is valid, False otherwise
        """
        if not response or not response.strip():
            logger.warning("Empty response from agent")
            return False
        
        if len(response) > self.max_message_length:
            logger.warning(f"Response too long: {len(response)} characters")
            return False
        
        return True
    
    def process_user_input(self, user_input: str) -> str:
        """
        Process user input before adding to conversation.
        
        Args:
            user_input: Raw user input
            
        Returns:
            str: Processed user input
        """
        # Basic processing - can be overridden by subclasses
        processed = user_input.strip()
        
        # Truncate if necessary
        processed = self.truncate_message(processed)
        
        return processed
    
    def should_continue_conversation(self) -> bool:
        """
        Determine if the conversation should continue.
        
        Returns:
            bool: True if conversation should continue, False otherwise
        """
        if not self.conversation_active:
            return False
        
        if self.is_max_turns_reached():
            logger.info("Maximum turns reached, ending conversation")
            return False
        
        return True
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get conversation statistics.
        
        Returns:
            Dict containing conversation statistics
        """
        user_messages = sum(1 for msg in self.messages if msg.role == "user")
        assistant_messages = sum(1 for msg in self.messages if msg.role == "assistant")
        system_messages = sum(1 for msg in self.messages if msg.role == "system")
        
        total_chars = sum(len(msg.content) for msg in self.messages)
        avg_message_length = total_chars / len(self.messages) if self.messages else 0
        
        return {
            "total_messages": len(self.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "system_messages": system_messages,
            "total_characters": total_chars,
            "average_message_length": avg_message_length,
            "conversation_active": self.conversation_active,
            "current_turn": self.current_turn,
            "max_turns": self.max_turns
        }
    
    def reset_conversation(self):
        """Reset the conversation state."""
        self.messages.clear()
        self.conversation_history.clear()
        self.current_query = ""
        self.current_response = ""
        self.conversation_active = False
        self.current_turn = 0
        
        logger.debug("Conversation state reset")
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get the conversation messages for the agent.
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history
