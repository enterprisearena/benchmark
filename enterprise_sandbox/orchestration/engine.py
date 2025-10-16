"""
Orchestration Engine

This module implements the orchestration engine for cross-platform workflows.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from enum import Enum

from ..platforms.base.platform import BasePlatform
from ..platforms.base.exceptions import OrchestrationError

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Enumeration of task step statuses."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ValidationRule:
    """Validation rule for task steps."""
    
    def __init__(self, rule_type: str, parameters: Dict[str, Any]):
        self.rule_type = rule_type
        self.parameters = parameters


class ErrorHandlingStrategy:
    """Error handling strategy for task steps."""
    
    def __init__(self, strategy: str, parameters: Dict[str, Any]):
        self.strategy = strategy  # "retry", "skip", "fail", "continue"
        self.parameters = parameters


@dataclass
class TaskStep:
    """Data class for individual task steps."""
    step_id: str
    name: str
    platform: str
    action_type: str
    parameters: Dict[str, Any]
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    validation_rules: List[ValidationRule] = field(default_factory=list)
    error_handling: ErrorHandlingStrategy = field(default_factory=lambda: ErrorHandlingStrategy("retry", {"max_retries": 3}))
    timeout_seconds: int = 60
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0


@dataclass
class CrossPlatformTask:
    """Data class for cross-platform tasks."""
    task_id: str
    name: str
    description: str
    category: str
    platforms: List[str]
    complexity: str
    steps: List[TaskStep]
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    expected_output: Any = None
    evaluation_metric: str = "completion"
    timeout_seconds: int = 300
    retry_attempts: int = 3
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)


class OrchestrationEngine:
    """
    Orchestration engine for executing cross-platform workflows.
    
    This engine manages the execution of complex workflows that span multiple
    enterprise software platforms, handling dependencies, error recovery, and
    context management.
    """
    
    def __init__(self, platform_connections: Dict[str, BasePlatform]):
        """
        Initialize the orchestration engine.
        
        Args:
            platform_connections: Dictionary of platform connections
        """
        self.platform_connections = platform_connections
        self.execution_context: Dict[str, Any] = {}
        self.active_tasks: Dict[str, CrossPlatformTask] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized orchestration engine with {len(platform_connections)} platforms")
    
    async def execute_task(self, task: CrossPlatformTask) -> Dict[str, Any]:
        """
        Execute a cross-platform task.
        
        Args:
            task: CrossPlatformTask to execute
            
        Returns:
            Dict containing execution results
        """
        try:
            task.start_time = datetime.now()
            task.status = TaskStatus.RUNNING
            self.active_tasks[task.task_id] = task
            
            logger.info(f"Starting execution of task: {task.name}")
            
            # Validate task dependencies
            self._validate_dependencies(task)
            
            # Sort steps by dependencies
            sorted_steps = self._topological_sort(task.steps, task.dependencies)
            
            # Execute steps in order
            results = {}
            for step in sorted_steps:
                try:
                    step_result = await self._execute_step(step, task)
                    results[step.step_id] = step_result
                    
                    # Update context with step results
                    self._update_context(step, step_result)
                    
                except Exception as e:
                    logger.error(f"Step {step.step_id} failed: {e}")
                    step.status = TaskStatus.FAILED
                    step.error = str(e)
                    
                    # Handle step failure based on error strategy
                    if step.error_handling.strategy == "fail":
                        raise OrchestrationError(f"Task failed at step {step.step_id}: {e}")
                    elif step.error_handling.strategy == "skip":
                        step.status = TaskStatus.SKIPPED
                        continue
                    # For "retry" and "continue", the step status remains FAILED
            
            # Generate final result
            final_result = self._generate_final_result(task)
            
            task.end_time = datetime.now()
            task.status = TaskStatus.COMPLETED
            task.results = results
            
            # Record execution
            self.execution_history.append({
                "task_id": task.task_id,
                "start_time": task.start_time,
                "end_time": task.end_time,
                "status": task.status.value,
                "results": results
            })
            
            logger.info(f"Task {task.name} completed successfully")
            return final_result
            
        except Exception as e:
            task.end_time = datetime.now()
            task.status = TaskStatus.FAILED
            
            logger.error(f"Task {task.name} failed: {e}")
            return self._handle_execution_error(e, task)
    
    async def _execute_step(self, step: TaskStep, task: CrossPlatformTask) -> Dict[str, Any]:
        """
        Execute a single task step.
        
        Args:
            step: TaskStep to execute
            task: Parent CrossPlatformTask
            
        Returns:
            Dict containing step execution results
        """
        step.start_time = datetime.now()
        step.status = TaskStatus.RUNNING
        
        logger.info(f"Executing step: {step.name} on platform {step.platform}")
        
        try:
            # Get platform connection
            platform = self.platform_connections.get(step.platform)
            if not platform:
                raise OrchestrationError(f"Platform {step.platform} not available")
            
            # Map input parameters from context
            mapped_parameters = self._map_input_parameters(step, task)
            
            # Execute the action
            if step.action_type == "query":
                result = await platform.execute_query(
                    mapped_parameters.get("query", ""),
                    mapped_parameters.get("parameters")
                )
            elif step.action_type == "create":
                result = await platform.create_record(
                    mapped_parameters.get("object_type", ""),
                    mapped_parameters.get("data", {})
                )
            elif step.action_type == "update":
                result = await platform.update_record(
                    mapped_parameters.get("object_type", ""),
                    mapped_parameters.get("record_id", ""),
                    mapped_parameters.get("data", {})
                )
            elif step.action_type == "delete":
                result = await platform.delete_record(
                    mapped_parameters.get("object_type", ""),
                    mapped_parameters.get("record_id", "")
                )
            elif step.action_type == "search":
                result = await platform.search_records(
                    mapped_parameters.get("object_type", ""),
                    mapped_parameters.get("criteria", {})
                )
            else:
                raise OrchestrationError(f"Unknown action type: {step.action_type}")
            
            # Validate result
            self._validate_step_result(step, result)
            
            step.end_time = datetime.now()
            step.status = TaskStatus.COMPLETED
            step.result = {
                "success": result.success,
                "data": result.data,
                "execution_time": result.execution_time,
                "metadata": getattr(result, 'metadata', {})
            }
            
            return step.result
            
        except Exception as e:
            step.end_time = datetime.now()
            step.status = TaskStatus.FAILED
            step.error = str(e)
            
            # Handle retry logic
            if step.error_handling.strategy == "retry" and step.retry_count < step.error_handling.parameters.get("max_retries", 3):
                step.retry_count += 1
                logger.warning(f"Step {step.step_id} failed, retrying ({step.retry_count}/{step.error_handling.parameters.get('max_retries', 3)})")
                
                # Wait before retry
                await asyncio.sleep(step.error_handling.parameters.get("retry_delay", 1))
                
                # Reset step status and retry
                step.status = TaskStatus.PENDING
                return await self._execute_step(step, task)
            
            raise
    
    def _validate_dependencies(self, task: CrossPlatformTask):
        """
        Validate task dependencies.
        
        Args:
            task: CrossPlatformTask to validate
            
        Raises:
            OrchestrationError: If dependencies are invalid
        """
        step_ids = {step.step_id for step in task.steps}
        
        for step_id, dependencies in task.dependencies.items():
            if step_id not in step_ids:
                raise OrchestrationError(f"Step {step_id} referenced in dependencies but not found in task steps")
            
            for dep_id in dependencies:
                if dep_id not in step_ids:
                    raise OrchestrationError(f"Dependency {dep_id} for step {step_id} not found in task steps")
    
    def _topological_sort(self, steps: List[TaskStep], dependencies: Dict[str, List[str]]) -> List[TaskStep]:
        """
        Sort steps by dependencies using topological sort.
        
        Args:
            steps: List of task steps
            dependencies: Dependency mapping
            
        Returns:
            List of steps sorted by dependencies
        """
        # Create step lookup
        step_lookup = {step.step_id: step for step in steps}
        
        # Build dependency graph
        in_degree = {step.step_id: 0 for step in steps}
        graph = {step.step_id: [] for step in steps}
        
        for step_id, deps in dependencies.items():
            for dep_id in deps:
                graph[dep_id].append(step_id)
                in_degree[step_id] += 1
        
        # Topological sort using Kahn's algorithm
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        sorted_steps = []
        
        while queue:
            current_step_id = queue.pop(0)
            sorted_steps.append(step_lookup[current_step_id])
            
            for dependent_step_id in graph[current_step_id]:
                in_degree[dependent_step_id] -= 1
                if in_degree[dependent_step_id] == 0:
                    queue.append(dependent_step_id)
        
        # Check for cycles
        if len(sorted_steps) != len(steps):
            raise OrchestrationError("Circular dependency detected in task steps")
        
        return sorted_steps
    
    def _map_input_parameters(self, step: TaskStep, task: CrossPlatformTask) -> Dict[str, Any]:
        """
        Map input parameters from execution context.
        
        Args:
            step: TaskStep to map parameters for
            task: Parent CrossPlatformTask
            
        Returns:
            Dict containing mapped parameters
        """
        mapped_params = step.parameters.copy()
        
        # Map parameters from context
        for context_key, param_key in step.input_mapping.items():
            if context_key in self.execution_context:
                mapped_params[param_key] = self.execution_context[context_key]
        
        return mapped_params
    
    def _update_context(self, step: TaskStep, result: Dict[str, Any]):
        """
        Update execution context with step results.
        
        Args:
            step: Completed TaskStep
            result: Step execution result
        """
        # Map output parameters to context
        for output_key, context_key in step.output_mapping.items():
            if output_key in result:
                self.execution_context[context_key] = result[output_key]
        
        # Store step result in context
        self.execution_context[f"step_{step.step_id}_result"] = result
    
    def _validate_step_result(self, step: TaskStep, result: Any):
        """
        Validate step execution result.
        
        Args:
            step: TaskStep that was executed
            result: Execution result
            
        Raises:
            OrchestrationError: If validation fails
        """
        for rule in step.validation_rules:
            if rule.rule_type == "success_required" and not result.success:
                raise OrchestrationError(f"Step {step.step_id} failed validation: success required")
            
            elif rule.rule_type == "data_required" and not result.data:
                raise OrchestrationError(f"Step {step.step_id} failed validation: data required")
            
            elif rule.rule_type == "field_required":
                required_field = rule.parameters.get("field")
                if required_field and (not result.data or required_field not in result.data):
                    raise OrchestrationError(f"Step {step.step_id} failed validation: field {required_field} required")
    
    def _generate_final_result(self, task: CrossPlatformTask) -> Dict[str, Any]:
        """
        Generate final result for the task.
        
        Args:
            task: Completed CrossPlatformTask
            
        Returns:
            Dict containing final task result
        """
        execution_time = (task.end_time - task.start_time).total_seconds() if task.end_time and task.start_time else 0
        
        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "execution_time": execution_time,
            "steps_completed": sum(1 for step in task.steps if step.status == TaskStatus.COMPLETED),
            "steps_failed": sum(1 for step in task.steps if step.status == TaskStatus.FAILED),
            "steps_skipped": sum(1 for step in task.steps if step.status == TaskStatus.SKIPPED),
            "total_steps": len(task.steps),
            "results": task.results,
            "context": self.execution_context.copy()
        }
    
    def _handle_execution_error(self, error: Exception, task: CrossPlatformTask) -> Dict[str, Any]:
        """
        Handle execution errors.
        
        Args:
            error: Exception that occurred
            task: CrossPlatformTask that failed
            
        Returns:
            Dict containing error information
        """
        execution_time = (datetime.now() - task.start_time).total_seconds() if task.start_time else 0
        
        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": "failed",
            "execution_time": execution_time,
            "error": str(error),
            "steps_completed": sum(1 for step in task.steps if step.status == TaskStatus.COMPLETED),
            "steps_failed": sum(1 for step in task.steps if step.status == TaskStatus.FAILED),
            "total_steps": len(task.steps)
        }
    
    def get_execution_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution status for a task.
        
        Args:
            task_id: Task ID to get status for
            
        Returns:
            Dict containing task status if found, None otherwise
        """
        task = self.active_tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task_id,
            "status": task.status.value,
            "start_time": task.start_time,
            "current_step": next((step for step in task.steps if step.status == TaskStatus.RUNNING), None),
            "progress": sum(1 for step in task.steps if step.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]) / len(task.steps)
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get execution history.
        
        Returns:
            List of execution history entries
        """
        return self.execution_history.copy()
    
    def clear_context(self):
        """Clear the execution context."""
        self.execution_context.clear()
        logger.debug("Execution context cleared")
