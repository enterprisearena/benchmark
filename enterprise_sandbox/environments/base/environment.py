"""
Base Environment Implementation

This module defines the abstract base class and data structures for all environment
implementations in EnterpriseArena.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EnvironmentState(Enum):
    """Enumeration of environment states."""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    TERMINATED = "terminated"


class EnvironmentType(Enum):
    """Enumeration of environment types."""
    SINGLE_PLATFORM = "single_platform"
    CROSS_PLATFORM = "cross_platform"
    INTERACTIVE = "interactive"
    CHAT = "chat"
    TOOL = "tool"


@dataclass
class EnvironmentResult:
    """Data class for environment execution results."""
    observation: str
    reward: float
    done: bool
    info: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    execution_time: float = 0.0
    step_count: int = 0


@dataclass
class EnvironmentInfo:
    """Data class for environment information."""
    environment_type: EnvironmentType
    platform: Optional[str] = None
    platforms: List[str] = field(default_factory=list)
    task_count: int = 0
    current_task: Optional[int] = None
    state: EnvironmentState = EnvironmentState.INITIALIZED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class BaseEnvironment(ABC):
    """
    Abstract base class for all environment implementations.
    
    This class defines the interface that all environments must implement to ensure
    consistent behavior across different environment types and platforms.
    """
    
    def __init__(self, tasks: Dict[int, Dict], **kwargs):
        """
        Initialize the environment.
        
        Args:
            tasks: Dictionary of tasks indexed by task ID
            **kwargs: Additional environment-specific parameters
        """
        self.tasks = tasks
        self.environment_type = kwargs.get("environment_type", EnvironmentType.SINGLE_PLATFORM)
        self.max_steps = kwargs.get("max_steps", 100)
        self.timeout_seconds = kwargs.get("timeout_seconds", 300)
        self.enable_logging = kwargs.get("enable_logging", True)
        self.debug_mode = kwargs.get("debug_mode", False)
        
        # Environment state
        self.state = EnvironmentState.INITIALIZED
        self.current_task_index: Optional[int] = None
        self.current_step = 0
        self.total_reward = 0.0
        self.done = False
        
        # Execution tracking
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.execution_history: List[Dict[str, Any]] = []
        self.step_history: List[EnvironmentResult] = []
        
        # Environment info
        self.info = EnvironmentInfo(
            environment_type=self.environment_type,
            task_count=len(tasks),
            state=self.state
        )
        
        logger.info(f"Initialized {self.environment_type.value} environment with {len(tasks)} tasks")
    
    @abstractmethod
    def reset(self, task_index: int) -> Tuple[str, Dict[str, Any]]:
        """
        Reset the environment for a new task.
        
        Args:
            task_index: Index of the task to start
            
        Returns:
            Tuple of (initial_observation, info)
        """
        pass
    
    @abstractmethod
    def step(self, action: Dict[str, Any]) -> Tuple[str, float, bool, Dict[str, Any]]:
        """
        Execute a step in the environment.
        
        Args:
            action: Action to execute
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        pass
    
    def get_task(self, task_index: int) -> Dict[str, Any]:
        """
        Get a task by index.
        
        Args:
            task_index: Index of the task
            
        Returns:
            Task dictionary
        """
        return self.tasks.get(task_index, {})
    
    def get_available_tasks(self) -> List[int]:
        """
        Get list of available task indices.
        
        Returns:
            List of task indices
        """
        return list(self.tasks.keys())
    
    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """
        Get the current task.
        
        Returns:
            Current task dictionary if available, None otherwise
        """
        if self.current_task_index is not None:
            return self.get_task(self.current_task_index)
        return None
    
    def is_task_available(self, task_index: int) -> bool:
        """
        Check if a task is available.
        
        Args:
            task_index: Index of the task to check
            
        Returns:
            bool: True if task is available, False otherwise
        """
        return task_index in self.tasks
    
    def get_environment_info(self) -> EnvironmentInfo:
        """
        Get environment information.
        
        Returns:
            EnvironmentInfo object
        """
        self.info.current_task = self.current_task_index
        self.info.state = self.state
        self.info.start_time = self.start_time
        self.info.end_time = self.end_time
        return self.info
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dict containing execution statistics
        """
        execution_time = 0.0
        if self.start_time:
            end_time = self.end_time or datetime.now()
            execution_time = (end_time - self.start_time).total_seconds()
        
        return {
            "current_task": self.current_task_index,
            "current_step": self.current_step,
            "total_reward": self.total_reward,
            "execution_time": execution_time,
            "total_steps": len(self.step_history),
            "state": self.state.value,
            "done": self.done
        }
    
    def get_step_history(self) -> List[EnvironmentResult]:
        """
        Get the step execution history.
        
        Returns:
            List of EnvironmentResult objects
        """
        return self.step_history.copy()
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get the execution history.
        
        Returns:
            List of execution history entries
        """
        return self.execution_history.copy()
    
    def start_execution(self, task_index: int):
        """
        Start execution of a task.
        
        Args:
            task_index: Index of the task to start
        """
        self.start_time = datetime.now()
        self.state = EnvironmentState.RUNNING
        self.current_task_index = task_index
        self.current_step = 0
        self.total_reward = 0.0
        self.done = False
        self.step_history.clear()
        
        logger.info(f"Started execution of task {task_index}")
    
    def end_execution(self):
        """End execution of the current task."""
        self.end_time = datetime.now()
        self.state = EnvironmentState.COMPLETED
        self.done = True
        
        # Record execution
        execution_time = (self.end_time - self.start_time).total_seconds() if self.start_time else 0.0
        self.execution_history.append({
            "task_index": self.current_task_index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": execution_time,
            "total_steps": self.current_step,
            "total_reward": self.total_reward,
            "state": self.state.value
        })
        
        logger.info(f"Ended execution of task {self.current_task_index} in {execution_time:.2f}s")
    
    def pause_execution(self):
        """Pause execution of the current task."""
        self.state = EnvironmentState.PAUSED
        logger.info("Execution paused")
    
    def resume_execution(self):
        """Resume execution of the current task."""
        self.state = EnvironmentState.RUNNING
        logger.info("Execution resumed")
    
    def terminate_execution(self):
        """Terminate execution of the current task."""
        self.end_time = datetime.now()
        self.state = EnvironmentState.TERMINATED
        self.done = True
        logger.info("Execution terminated")
    
    def handle_error(self, error: Exception, context: str = "") -> EnvironmentResult:
        """
        Handle an error during environment execution.
        
        Args:
            error: Exception that occurred
            context: Context where the error occurred
            
        Returns:
            EnvironmentResult: Error result
        """
        error_message = f"Error in {context}: {str(error)}"
        logger.error(error_message)
        
        self.state = EnvironmentState.ERROR
        self.done = True
        
        return EnvironmentResult(
            observation="Environment error occurred",
            reward=0.0,
            done=True,
            info={"error": error_message},
            success=False,
            error_message=error_message
        )
    
    def validate_action(self, action: Dict[str, Any]) -> bool:
        """
        Validate an action before execution.
        
        Args:
            action: Action to validate
            
        Returns:
            bool: True if action is valid, False otherwise
        """
        if not isinstance(action, dict):
            logger.warning("Action must be a dictionary")
            return False
        
        if not action:
            logger.warning("Action cannot be empty")
            return False
        
        return True
    
    def calculate_reward(self, action: Dict[str, Any], result: Any) -> float:
        """
        Calculate reward for an action and result.
        
        Args:
            action: Action that was taken
            result: Result of the action
            
        Returns:
            float: Calculated reward
        """
        # Base implementation - can be overridden by subclasses
        if isinstance(result, EnvironmentResult):
            return result.reward
        return 0.0
    
    def is_max_steps_reached(self) -> bool:
        """
        Check if maximum steps have been reached.
        
        Returns:
            bool: True if max steps reached, False otherwise
        """
        return self.current_step >= self.max_steps
    
    def is_timeout_reached(self) -> bool:
        """
        Check if timeout has been reached.
        
        Returns:
            bool: True if timeout reached, False otherwise
        """
        if not self.start_time:
            return False
        
        execution_time = (datetime.now() - self.start_time).total_seconds()
        return execution_time >= self.timeout_seconds
    
    def should_terminate(self) -> bool:
        """
        Check if execution should be terminated.
        
        Returns:
            bool: True if should terminate, False otherwise
        """
        return self.done or self.is_max_steps_reached() or self.is_timeout_reached()
    
    def log_step(self, action: Dict[str, Any], result: EnvironmentResult):
        """
        Log a step execution.
        
        Args:
            action: Action that was taken
            result: Result of the action
        """
        if not self.enable_logging:
            return
        
        log_entry = {
            "step": self.current_step,
            "action": action,
            "result": {
                "observation": result.observation,
                "reward": result.reward,
                "done": result.done,
                "success": result.success
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if self.debug_mode:
            log_entry["info"] = result.info
        
        logger.debug(f"Step {self.current_step}: {log_entry}")
    
    def reset_environment(self):
        """Reset the environment to initial state."""
        self.state = EnvironmentState.INITIALIZED
        self.current_task_index = None
        self.current_step = 0
        self.total_reward = 0.0
        self.done = False
        self.start_time = None
        self.end_time = None
        self.step_history.clear()
        
        logger.info("Environment reset to initial state")
    
    def __str__(self) -> str:
        """String representation of the environment."""
        return f"{self.environment_type.value.title()}Environment(tasks={len(self.tasks)}, state={self.state.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the environment."""
        return (f"{self.__class__.__name__}("
                f"environment_type={self.environment_type.value}, "
                f"tasks={len(self.tasks)}, "
                f"state={self.state.value}, "
                f"current_task={self.current_task_index})")
