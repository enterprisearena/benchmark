"""
Single Platform Environment Base Class

This module provides the base class for single-platform environments.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from .environment import BaseEnvironment, EnvironmentResult, EnvironmentState, EnvironmentType

logger = logging.getLogger(__name__)


class SinglePlatformEnvironment(BaseEnvironment):
    """
    Base class for single-platform environments.
    
    This class provides common functionality for environments that interact
    with a single enterprise software platform.
    """
    
    def __init__(self, tasks: Dict[int, Dict], platform: str, **kwargs):
        """
        Initialize the single-platform environment.
        
        Args:
            tasks: Dictionary of tasks indexed by task ID
            platform: Platform name (e.g., 'salesforce', 'servicenow')
            **kwargs: Additional environment-specific parameters
        """
        super().__init__(tasks, **kwargs)
        self.environment_type = EnvironmentType.SINGLE_PLATFORM
        self.platform = platform
        
        # Platform-specific configuration
        self.platform_config = kwargs.get("platform_config", {})
        self.schema_info = kwargs.get("schema_info", {})
        self.connection_pool = kwargs.get("connection_pool", None)
        
        # Single-platform specific state
        self.platform_connection = None
        self.current_query = ""
        self.query_history: List[Dict[str, Any]] = []
        self.action_history: List[Dict[str, Any]] = []
        
        # Update environment info
        self.info.platform = platform
        
        logger.info(f"Initialized single-platform environment for {platform}")
    
    def set_platform_connection(self, connection):
        """
        Set the platform connection.
        
        Args:
            connection: Platform connection object
        """
        self.platform_connection = connection
        logger.debug(f"Platform connection set for {self.platform}")
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get platform-specific information.
        
        Returns:
            Dict containing platform information
        """
        return {
            "platform": self.platform,
            "platform_config": self.platform_config,
            "schema_info": self.schema_info,
            "connection_available": self.platform_connection is not None
        }
    
    def validate_platform_action(self, action: Dict[str, Any]) -> bool:
        """
        Validate an action for the specific platform.
        
        Args:
            action: Action to validate
            
        Returns:
            bool: True if action is valid for the platform, False otherwise
        """
        if not self.validate_action(action):
            return False
        
        # Platform-specific validation
        action_type = action.get("action_type")
        if not action_type:
            logger.warning("Action must specify action_type")
            return False
        
        # Validate action type for platform
        valid_action_types = self._get_valid_action_types()
        if action_type not in valid_action_types:
            logger.warning(f"Invalid action_type '{action_type}' for platform {self.platform}")
            return False
        
        # Validate action parameters
        return self._validate_action_parameters(action)
    
    def _get_valid_action_types(self) -> List[str]:
        """
        Get valid action types for the platform.
        
        Returns:
            List of valid action types
        """
        return ["query", "create", "update", "delete", "search", "execute"]
    
    def _validate_action_parameters(self, action: Dict[str, Any]) -> bool:
        """
        Validate action parameters for the platform.
        
        Args:
            action: Action to validate
            
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        action_type = action.get("action_type")
        
        if action_type == "query":
            return "query" in action or "object_type" in action
        elif action_type in ["create", "update"]:
            return "object_type" in action and "data" in action
        elif action_type == "delete":
            return "object_type" in action and "record_id" in action
        elif action_type == "search":
            return "object_type" in action and "criteria" in action
        elif action_type == "execute":
            return "function" in action
        
        return True
    
    def format_platform_response(self, response: Any) -> str:
        """
        Format platform response for display.
        
        Args:
            response: Raw platform response
            
        Returns:
            str: Formatted response string
        """
        if isinstance(response, dict):
            if response.get("success", False):
                data = response.get("data", [])
                if isinstance(data, list) and data:
                    return f"Query returned {len(data)} records: {data[:3]}..."  # Show first 3 records
                elif isinstance(data, dict):
                    return f"Operation successful: {data}"
                else:
                    return "Operation completed successfully"
            else:
                error = response.get("error_message", "Unknown error")
                return f"Operation failed: {error}"
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    def record_query(self, query: str, result: Any):
        """
        Record a query execution.
        
        Args:
            query: Query that was executed
            result: Query result
        """
        self.query_history.append({
            "query": query,
            "result": result,
            "timestamp": datetime.now(),
            "step": self.current_step
        })
        
        # Keep only last 50 queries
        if len(self.query_history) > 50:
            self.query_history = self.query_history[-50:]
    
    def record_action(self, action: Dict[str, Any], result: Any):
        """
        Record an action execution.
        
        Args:
            action: Action that was executed
            result: Action result
        """
        self.action_history.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now(),
            "step": self.current_step
        })
        
        # Keep only last 50 actions
        if len(self.action_history) > 50:
            self.action_history = self.action_history[-50:]
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """
        Get query execution history.
        
        Returns:
            List of query history entries
        """
        return self.query_history.copy()
    
    def get_action_history(self) -> List[Dict[str, Any]]:
        """
        Get action execution history.
        
        Returns:
            List of action history entries
        """
        return self.action_history.copy()
    
    def get_platform_schema(self) -> Dict[str, Any]:
        """
        Get platform schema information.
        
        Returns:
            Dict containing platform schema
        """
        return self.schema_info
    
    def update_schema_info(self, schema_info: Dict[str, Any]):
        """
        Update platform schema information.
        
        Args:
            schema_info: New schema information
        """
        self.schema_info.update(schema_info)
        logger.debug(f"Updated schema info for {self.platform}")
    
    def calculate_platform_reward(self, action: Dict[str, Any], result: Any) -> float:
        """
        Calculate reward based on platform-specific criteria.
        
        Args:
            action: Action that was taken
            result: Result of the action
            
        Returns:
            float: Calculated reward
        """
        base_reward = self.calculate_reward(action, result)
        
        # Platform-specific reward adjustments
        if isinstance(result, EnvironmentResult):
            if result.success:
                # Bonus for successful operations
                if action.get("action_type") == "query" and result.data:
                    # Bonus for returning data
                    data_count = len(result.data) if isinstance(result.data, list) else 1
                    base_reward += min(data_count * 0.1, 1.0)
                elif action.get("action_type") in ["create", "update"]:
                    # Bonus for successful modifications
                    base_reward += 0.5
            else:
                # Penalty for failed operations
                base_reward -= 0.5
        
        return base_reward
    
    def get_platform_metrics(self) -> Dict[str, Any]:
        """
        Get platform-specific metrics.
        
        Returns:
            Dict containing platform metrics
        """
        return {
            "platform": self.platform,
            "queries_executed": len(self.query_history),
            "actions_executed": len(self.action_history),
            "successful_queries": sum(1 for q in self.query_history if q["result"].get("success", False)),
            "successful_actions": sum(1 for a in self.action_history if a["result"].get("success", False)),
            "connection_status": "connected" if self.platform_connection else "disconnected"
        }
    
    def reset_platform_state(self):
        """Reset platform-specific state."""
        self.current_query = ""
        self.query_history.clear()
        self.action_history.clear()
        logger.debug(f"Reset platform state for {self.platform}")
    
    def reset_environment(self):
        """Reset the environment to initial state."""
        super().reset_environment()
        self.reset_platform_state()
        logger.info(f"Reset single-platform environment for {self.platform}")
