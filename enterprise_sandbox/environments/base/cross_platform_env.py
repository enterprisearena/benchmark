"""
Cross Platform Environment Base Class

This module provides the base class for cross-platform environments.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from .environment import BaseEnvironment, EnvironmentResult, EnvironmentState, EnvironmentType

logger = logging.getLogger(__name__)


class CrossPlatformEnvironment(BaseEnvironment):
    """
    Base class for cross-platform environments.
    
    This class provides common functionality for environments that coordinate
    workflows across multiple enterprise software platforms.
    """
    
    def __init__(self, tasks: Dict[int, Dict], platforms: List[str], **kwargs):
        """
        Initialize the cross-platform environment.
        
        Args:
            tasks: Dictionary of tasks indexed by task ID
            platforms: List of platform names involved
            **kwargs: Additional environment-specific parameters
        """
        super().__init__(tasks, **kwargs)
        self.environment_type = EnvironmentType.CROSS_PLATFORM
        self.platforms = platforms
        
        # Cross-platform specific configuration
        self.platform_connections: Dict[str, Any] = {}
        self.orchestration_engine = kwargs.get("orchestration_engine", None)
        self.workflow_manager = kwargs.get("workflow_manager", None)
        
        # Cross-platform specific state
        self.current_workflow: Optional[Dict[str, Any]] = None
        self.workflow_history: List[Dict[str, Any]] = []
        self.platform_coordination: Dict[str, Any] = {}
        self.data_flow: Dict[str, Any] = {}
        
        # Update environment info
        self.info.platforms = platforms
        
        logger.info(f"Initialized cross-platform environment for platforms: {platforms}")
    
    def set_platform_connections(self, connections: Dict[str, Any]):
        """
        Set platform connections.
        
        Args:
            connections: Dictionary of platform connections
        """
        self.platform_connections = connections
        logger.debug(f"Set platform connections for: {list(connections.keys())}")
    
    def set_orchestration_engine(self, engine):
        """
        Set the orchestration engine.
        
        Args:
            engine: OrchestrationEngine instance
        """
        self.orchestration_engine = engine
        logger.debug("Set orchestration engine")
    
    def set_workflow_manager(self, manager):
        """
        Set the workflow manager.
        
        Args:
            manager: WorkflowManager instance
        """
        self.workflow_manager = manager
        logger.debug("Set workflow manager")
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get cross-platform information.
        
        Returns:
            Dict containing platform information
        """
        return {
            "platforms": self.platforms,
            "platform_connections": list(self.platform_connections.keys()),
            "orchestration_engine_available": self.orchestration_engine is not None,
            "workflow_manager_available": self.workflow_manager is not None,
            "current_workflow": self.current_workflow is not None
        }
    
    def validate_cross_platform_action(self, action: Dict[str, Any]) -> bool:
        """
        Validate an action for cross-platform execution.
        
        Args:
            action: Action to validate
            
        Returns:
            bool: True if action is valid, False otherwise
        """
        if not self.validate_action(action):
            return False
        
        # Cross-platform specific validation
        action_type = action.get("action_type")
        if not action_type:
            logger.warning("Action must specify action_type")
            return False
        
        # Validate cross-platform action types
        valid_action_types = self._get_valid_cross_platform_action_types()
        if action_type not in valid_action_types:
            logger.warning(f"Invalid action_type '{action_type}' for cross-platform environment")
            return False
        
        # Validate platform coordination
        if "platforms" in action:
            platforms = action["platforms"]
            if not isinstance(platforms, list):
                logger.warning("Platforms must be a list")
                return False
            
            for platform in platforms:
                if platform not in self.platforms:
                    logger.warning(f"Platform '{platform}' not available in environment")
                    return False
        
        return True
    
    def _get_valid_cross_platform_action_types(self) -> List[str]:
        """
        Get valid action types for cross-platform execution.
        
        Returns:
            List of valid action types
        """
        return [
            "orchestrate", "coordinate", "workflow", "sync", "integrate",
            "query_cross_platform", "create_cross_platform", "update_cross_platform",
            "data_flow", "platform_handoff", "multi_platform_query"
        ]
    
    def execute_cross_platform_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a cross-platform workflow.
        
        Args:
            workflow: Workflow definition
            
        Returns:
            Dict containing workflow execution results
        """
        if not self.orchestration_engine:
            raise ValueError("Orchestration engine not available")
        
        try:
            # Record workflow start
            self.current_workflow = workflow
            workflow_start_time = datetime.now()
            
            # Execute workflow using orchestration engine
            result = self.orchestration_engine.execute_task(workflow)
            
            # Record workflow completion
            workflow_end_time = datetime.now()
            workflow_duration = (workflow_end_time - workflow_start_time).total_seconds()
            
            workflow_record = {
                "workflow": workflow,
                "result": result,
                "start_time": workflow_start_time,
                "end_time": workflow_end_time,
                "duration": workflow_duration,
                "step": self.current_step
            }
            
            self.workflow_history.append(workflow_record)
            
            # Keep only last 20 workflows
            if len(self.workflow_history) > 20:
                self.workflow_history = self.workflow_history[-20:]
            
            logger.info(f"Executed cross-platform workflow in {workflow_duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Cross-platform workflow execution failed: {e}")
            raise
    
    def coordinate_platforms(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate actions across multiple platforms.
        
        Args:
            coordination_request: Coordination request
            
        Returns:
            Dict containing coordination results
        """
        try:
            platforms = coordination_request.get("platforms", [])
            actions = coordination_request.get("actions", {})
            
            results = {}
            
            for platform in platforms:
                if platform in self.platform_connections:
                    platform_connection = self.platform_connections[platform]
                    platform_action = actions.get(platform)
                    
                    if platform_action:
                        # Execute platform-specific action
                        platform_result = self._execute_platform_action(
                            platform_connection, platform_action
                        )
                        results[platform] = platform_result
                    else:
                        results[platform] = {"error": "No action specified for platform"}
                else:
                    results[platform] = {"error": f"Platform {platform} not available"}
            
            # Record coordination
            self.platform_coordination[f"coordination_{self.current_step}"] = {
                "request": coordination_request,
                "results": results,
                "timestamp": datetime.now()
            }
            
            return {
                "success": all(
                    result.get("success", False) for result in results.values()
                    if "error" not in result
                ),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Platform coordination failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_platform_action(self, platform_connection, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action on a specific platform.
        
        Args:
            platform_connection: Platform connection object
            action: Action to execute
            
        Returns:
            Dict containing action result
        """
        try:
            action_type = action.get("action_type")
            
            if action_type == "query":
                result = platform_connection.execute_query(
                    action.get("query", ""),
                    action.get("parameters")
                )
            elif action_type == "create":
                result = platform_connection.create_record(
                    action.get("object_type", ""),
                    action.get("data", {})
                )
            elif action_type == "update":
                result = platform_connection.update_record(
                    action.get("object_type", ""),
                    action.get("record_id", ""),
                    action.get("data", {})
                )
            elif action_type == "search":
                result = platform_connection.search_records(
                    action.get("object_type", ""),
                    action.get("criteria", {})
                )
            else:
                return {"success": False, "error": f"Unknown action type: {action_type}"}
            
            return {
                "success": result.success,
                "data": result.data,
                "execution_time": result.execution_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def manage_data_flow(self, data_flow_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage data flow between platforms.
        
        Args:
            data_flow_request: Data flow request
            
        Returns:
            Dict containing data flow results
        """
        try:
            source_platform = data_flow_request.get("source_platform")
            target_platform = data_flow_request.get("target_platform")
            data = data_flow_request.get("data")
            transformation = data_flow_request.get("transformation")
            
            # Validate platforms
            if source_platform not in self.platform_connections:
                return {"success": False, "error": f"Source platform {source_platform} not available"}
            
            if target_platform not in self.platform_connections:
                return {"success": False, "error": f"Target platform {target_platform} not available"}
            
            # Transform data if needed
            if transformation:
                transformed_data = self._transform_data(data, transformation)
            else:
                transformed_data = data
            
            # Record data flow
            flow_id = f"flow_{self.current_step}_{source_platform}_to_{target_platform}"
            self.data_flow[flow_id] = {
                "source_platform": source_platform,
                "target_platform": target_platform,
                "original_data": data,
                "transformed_data": transformed_data,
                "timestamp": datetime.now()
            }
            
            return {
                "success": True,
                "flow_id": flow_id,
                "transformed_data": transformed_data
            }
            
        except Exception as e:
            logger.error(f"Data flow management failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _transform_data(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """
        Transform data according to transformation rules.
        
        Args:
            data: Data to transform
            transformation: Transformation rules
            
        Returns:
            Transformed data
        """
        # Simple transformation implementation
        # Can be extended with more complex transformation logic
        
        if transformation.get("type") == "field_mapping":
            field_mapping = transformation.get("mapping", {})
            if isinstance(data, dict):
                transformed = {}
                for source_field, target_field in field_mapping.items():
                    if source_field in data:
                        transformed[target_field] = data[source_field]
                return transformed
        
        elif transformation.get("type") == "format_conversion":
            format_type = transformation.get("format")
            if format_type == "json_to_xml":
                # Simple JSON to XML conversion (would need proper implementation)
                return f"<data>{data}</data>"
        
        # Default: return data as-is
        return data
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """
        Get workflow execution history.
        
        Returns:
            List of workflow history entries
        """
        return self.workflow_history.copy()
    
    def get_platform_coordination_history(self) -> Dict[str, Any]:
        """
        Get platform coordination history.
        
        Returns:
            Dict containing coordination history
        """
        return self.platform_coordination.copy()
    
    def get_data_flow_history(self) -> Dict[str, Any]:
        """
        Get data flow history.
        
        Returns:
            Dict containing data flow history
        """
        return self.data_flow.copy()
    
    def get_cross_platform_metrics(self) -> Dict[str, Any]:
        """
        Get cross-platform specific metrics.
        
        Returns:
            Dict containing cross-platform metrics
        """
        return {
            "platforms": self.platforms,
            "workflows_executed": len(self.workflow_history),
            "coordination_events": len(self.platform_coordination),
            "data_flows": len(self.data_flow),
            "orchestration_engine_available": self.orchestration_engine is not None,
            "workflow_manager_available": self.workflow_manager is not None
        }
    
    def reset_cross_platform_state(self):
        """Reset cross-platform specific state."""
        self.current_workflow = None
        self.workflow_history.clear()
        self.platform_coordination.clear()
        self.data_flow.clear()
        logger.debug("Reset cross-platform state")
    
    def reset_environment(self):
        """Reset the environment to initial state."""
        super().reset_environment()
        self.reset_cross_platform_state()
        logger.info("Reset cross-platform environment")
