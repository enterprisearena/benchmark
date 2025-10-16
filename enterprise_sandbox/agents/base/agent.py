"""
Base Agent Implementation

This module defines the abstract base class and data structures for all agent
implementations in EnterpriseArena.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enumeration of supported agent types."""
    REACT = "react"
    TOOL_CALL = "tool_call"
    ORCHESTRATION = "orchestration"
    INTERACTIVE = "interactive"


class AgentState(Enum):
    """Enumeration of agent states."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentResult:
    """Data class for agent execution results."""
    success: bool
    reward: float = 0.0
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    steps_taken: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMessage:
    """Data class for agent messages."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations.
    
    This class defines the interface that all agents must implement to ensure
    consistent behavior across different agent types and strategies.
    """
    
    def __init__(self, model: str, **kwargs):
        """
        Initialize the agent.
        
        Args:
            model: LLM model to use for the agent
            **kwargs: Additional agent-specific parameters
        """
        self.model = model
        self.agent_type = kwargs.get("agent_type", AgentType.REACT)
        self.max_turns = kwargs.get("max_turns", 20)
        self.eval_mode = kwargs.get("eval_mode", "default")
        self.strategy = kwargs.get("strategy", "react")
        self.provider = kwargs.get("provider", "openai")
        self.interactive = kwargs.get("interactive", False)
        self.privacy_aware_prompt = kwargs.get("privacy_aware_prompt", False)
        
        # Agent state
        self.state = AgentState.IDLE
        self.current_turn = 0
        self.messages: List[AgentMessage] = []
        self.conversation_history: List[Dict[str, str]] = []
        self.execution_context: Dict[str, Any] = {}
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.total_execution_time = 0.0
        self.total_steps = 0
        
        logger.info(f"Initialized {self.agent_type.value} agent with model {model}")
    
    @abstractmethod
    def act(self, env, task_index: int) -> float:
        """
        Execute the agent's action in the environment.
        
        Args:
            env: Environment instance
            task_index: Index of the task to execute
            
        Returns:
            float: Reward received from the action
        """
        pass
    
    @abstractmethod
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get the conversation messages for the agent.
        
        Returns:
            List of message dictionaries
        """
        pass
    
    def reset(self, args: Dict[str, Any]):
        """
        Reset the agent state for a new task.
        
        Args:
            args: Reset arguments
        """
        self.state = AgentState.IDLE
        self.current_turn = 0
        self.messages.clear()
        self.conversation_history.clear()
        self.execution_context.clear()
        self.start_time = None
        self.total_execution_time = 0.0
        self.total_steps = 0
        
        logger.debug("Agent state reset")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the agent.
        
        Returns:
            Dict containing agent information
        """
        return {
            "agent_type": self.agent_type.value,
            "model": self.model,
            "strategy": self.strategy,
            "provider": self.provider,
            "max_turns": self.max_turns,
            "interactive": self.interactive,
            "privacy_aware_prompt": self.privacy_aware_prompt,
            "current_state": self.state.value,
            "current_turn": self.current_turn,
            "total_steps": self.total_steps,
            "total_execution_time": self.total_execution_time
        }
    
    def set_state(self, state: AgentState):
        """
        Set the agent state.
        
        Args:
            state: New agent state
        """
        old_state = self.state
        self.state = state
        logger.debug(f"Agent state changed from {old_state.value} to {state.value}")
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a message to the conversation.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional message metadata
        """
        message = AgentMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        
        # Also add to conversation history for compatibility
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation.
        
        Returns:
            str: Conversation summary
        """
        if not self.messages:
            return "No conversation yet."
        
        summary_parts = []
        for i, message in enumerate(self.messages):
            summary_parts.append(f"Turn {i+1} ({message.role}): {message.content[:100]}...")
        
        return "\n".join(summary_parts)
    
    def start_execution(self):
        """Start execution timing."""
        self.start_time = datetime.now()
        self.set_state(AgentState.THINKING)
        logger.debug("Agent execution started")
    
    def end_execution(self):
        """End execution timing."""
        if self.start_time:
            self.total_execution_time = (datetime.now() - self.start_time).total_seconds()
            self.set_state(AgentState.COMPLETED)
            logger.debug(f"Agent execution completed in {self.total_execution_time:.2f}s")
    
    def increment_turn(self):
        """Increment the current turn counter."""
        self.current_turn += 1
        self.total_steps += 1
        
        if self.current_turn >= self.max_turns:
            logger.warning(f"Agent reached maximum turns ({self.max_turns})")
            self.set_state(AgentState.ERROR)
    
    def is_max_turns_reached(self) -> bool:
        """
        Check if maximum turns have been reached.
        
        Returns:
            bool: True if max turns reached, False otherwise
        """
        return self.current_turn >= self.max_turns
    
    def create_result(self, success: bool, reward: float = 0.0, message: str = "", 
                     data: Dict[str, Any] = None, error_message: str = None) -> AgentResult:
        """
        Create an agent result.
        
        Args:
            success: Whether the action was successful
            reward: Reward received
            message: Result message
            data: Optional result data
            error_message: Optional error message
            
        Returns:
            AgentResult: Agent result object
        """
        return AgentResult(
            success=success,
            reward=reward,
            message=message,
            data=data or {},
            execution_time=self.total_execution_time,
            steps_taken=self.total_steps,
            error_message=error_message,
            metadata=self.execution_context.copy()
        )
    
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """
        Log an agent action.
        
        Args:
            action: Action description
            details: Optional action details
        """
        log_data = {
            "turn": self.current_turn,
            "state": self.state.value,
            "action": action
        }
        if details:
            log_data.update(details)
        
        logger.info(f"Agent action: {log_data}")
    
    def handle_error(self, error: Exception, context: str = "") -> AgentResult:
        """
        Handle an error during agent execution.
        
        Args:
            error: Exception that occurred
            context: Context where the error occurred
            
        Returns:
            AgentResult: Error result
        """
        error_message = f"Error in {context}: {str(error)}"
        logger.error(error_message)
        
        self.set_state(AgentState.ERROR)
        return self.create_result(
            success=False,
            reward=0.0,
            message="Agent execution failed",
            error_message=error_message
        )
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.agent_type.value.title()}Agent(model={self.model}, state={self.state.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (f"{self.__class__.__name__}("
                f"model={self.model}, "
                f"agent_type={self.agent_type.value}, "
                f"strategy={self.strategy}, "
                f"state={self.state.value}, "
                f"turns={self.current_turn}/{self.max_turns})")
