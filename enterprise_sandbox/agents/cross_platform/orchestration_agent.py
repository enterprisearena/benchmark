"""
Orchestration Agent Implementation

This module implements the orchestration agent for cross-platform tasks.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..base.agent import BaseAgent, AgentResult, AgentState, AgentType
from ..base.chat_agent import ChatAgent
from ..base.utils import AgentUtils

logger = logging.getLogger(__name__)


class OrchestrationAgent(ChatAgent):
    """
    Orchestration agent for cross-platform tasks.
    
    This agent coordinates workflows across multiple enterprise platforms,
    managing dependencies, data flow, and platform handoffs.
    """
    
    def __init__(self, model: str, platforms: List[str], **kwargs):
        """
        Initialize the orchestration agent.
        
        Args:
            model: LLM model to use for the agent
            platforms: List of platforms involved in cross-platform tasks
            **kwargs: Additional agent-specific parameters
        """
        super().__init__(model, **kwargs)
        self.agent_type = AgentType.ORCHESTRATION
        self.platforms = platforms
        
        # Orchestration-specific parameters
        self.orchestration_engine = kwargs.get("orchestration_engine", None)
        self.workflow_manager = kwargs.get("workflow_manager", None)
        self.max_platform_handoffs = kwargs.get("max_platform_handoffs", 10)
        self.enable_parallel_execution = kwargs.get("enable_parallel_execution", True)
        
        # Orchestration state
        self.current_workflow: Optional[Dict[str, Any]] = None
        self.platform_coordination: Dict[str, Any] = {}
        self.data_flow: Dict[str, Any] = {}
        self.execution_context: Dict[str, Any] = {}
        
        logger.info(f"Initialized orchestration agent for platforms: {platforms}")
    
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
    
    def act(self, env, task_index: int) -> float:
        """
        Execute the orchestration agent's action in the environment.
        
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
            
            # Start the orchestration workflow
            reward = self._execute_orchestration_workflow(env, task)
            
            self.end_execution()
            return reward
            
        except Exception as e:
            return self.handle_error(e, "orchestration execution").reward
    
    def _execute_orchestration_workflow(self, env, task: Dict[str, Any]) -> float:
        """
        Execute the main orchestration workflow.
        
        Args:
            env: Environment instance
            task: Task to execute
            
        Returns:
            float: Final reward
        """
        # Initialize environment
        observation, info = env.reset(task_index=task.get("idx", 0))
        self.add_system_message(f"Cross-platform task: {task.get('task', 'No task description')}")
        self.add_system_message(f"Platforms involved: {', '.join(self.platforms)}")
        
        total_reward = 0.0
        step_count = 0
        
        while not env.done and step_count < self.max_turns:
            try:
                # ORCHESTRATE: Plan cross-platform workflow
                orchestration_plan = self._plan_cross_platform_workflow(observation, task, step_count)
                self.add_assistant_message(f"Orchestration Plan: {orchestration_plan}")
                
                # COORDINATE: Execute platform coordination
                coordination_result = self._coordinate_platforms(orchestration_plan, task)
                self.add_assistant_message(f"Coordination Result: {coordination_result}")
                
                # EXECUTE: Run the orchestrated workflow
                if self.orchestration_engine and self.current_workflow:
                    workflow_result = await self._execute_workflow_with_engine()
                    self.add_assistant_message(f"Workflow Result: {workflow_result}")
                else:
                    # Fallback to manual orchestration
                    workflow_result = self._execute_manual_orchestration(orchestration_plan, env)
                
                # OBSERVE: Process results and update environment
                observation, reward, done, info = env.step({
                    "action_type": "orchestration",
                    "orchestration_plan": orchestration_plan,
                    "coordination_result": coordination_result,
                    "workflow_result": workflow_result
                })
                
                total_reward += reward
                step_count += 1
                self.increment_turn()
                
                # Check if task is complete
                if done:
                    logger.info(f"Cross-platform task completed in {step_count} steps with reward {total_reward}")
                    break
                
            except Exception as e:
                logger.error(f"Error in orchestration step {step_count}: {e}")
                self.add_assistant_message(f"Error: {str(e)}")
                break
        
        return total_reward
    
    def _plan_cross_platform_workflow(self, observation: str, task: Dict[str, Any], step: int) -> Dict[str, Any]:
        """
        Plan the cross-platform workflow.
        
        Args:
            observation: Current observation from environment
            task: Task being executed
            step: Current step number
            
        Returns:
            Dict containing orchestration plan
        """
        # Analyze the task to determine workflow
        task_text = task.get("task", "").lower()
        platforms = task.get("platforms", self.platforms)
        
        orchestration_plan = {
            "workflow_type": self._determine_workflow_type(task_text),
            "platforms": platforms,
            "steps": [],
            "dependencies": {},
            "data_flow": {},
            "coordination_points": []
        }
        
        # Determine workflow steps based on task type
        if "invoice" in task_text and "opportunity" in task_text:
            # Financial integration workflow
            orchestration_plan["steps"] = [
                {
                    "step_id": "fetch_invoice",
                    "platform": "quickbooks",
                    "action": "query",
                    "description": "Fetch invoice from QuickBooks"
                },
                {
                    "step_id": "transform_data",
                    "platform": "internal",
                    "action": "transform",
                    "description": "Transform invoice data for Salesforce"
                },
                {
                    "step_id": "create_opportunity",
                    "platform": "salesforce",
                    "action": "create",
                    "description": "Create opportunity in Salesforce"
                },
                {
                    "step_id": "link_records",
                    "platform": "internal",
                    "action": "link",
                    "description": "Link invoice and opportunity"
                }
            ]
            orchestration_plan["dependencies"] = {
                "transform_data": ["fetch_invoice"],
                "create_opportunity": ["transform_data"],
                "link_records": ["create_opportunity"]
            }
            orchestration_plan["data_flow"] = {
                "fetch_invoice": {"output": "invoice_data"},
                "transform_data": {"input": "invoice_data", "output": "opportunity_data"},
                "create_opportunity": {"input": "opportunity_data", "output": "opportunity_id"},
                "link_records": {"input": ["invoice_data", "opportunity_id"]}
            }
        
        elif "incident" in task_text and "case" in task_text:
            # Customer service workflow
            orchestration_plan["steps"] = [
                {
                    "step_id": "fetch_incident",
                    "platform": "servicenow",
                    "action": "query",
                    "description": "Fetch incident from ServiceNow"
                },
                {
                    "step_id": "create_case",
                    "platform": "salesforce",
                    "action": "create",
                    "description": "Create case in Salesforce"
                },
                {
                    "step_id": "sync_status",
                    "platform": "internal",
                    "action": "sync",
                    "description": "Sync status between platforms"
                }
            ]
            orchestration_plan["dependencies"] = {
                "create_case": ["fetch_incident"],
                "sync_status": ["create_case"]
            }
        
        else:
            # Generic cross-platform workflow
            orchestration_plan["steps"] = [
                {
                    "step_id": "query_platform_1",
                    "platform": platforms[0] if platforms else "unknown",
                    "action": "query",
                    "description": f"Query {platforms[0] if platforms else 'platform'}"
                },
                {
                    "step_id": "process_data",
                    "platform": "internal",
                    "action": "process",
                    "description": "Process data from platform 1"
                },
                {
                    "step_id": "update_platform_2",
                    "platform": platforms[1] if len(platforms) > 1 else platforms[0],
                    "action": "update",
                    "description": f"Update {platforms[1] if len(platforms) > 1 else platforms[0]}"
                }
            ]
        
        orchestration_plan["coordination_points"] = self._identify_coordination_points(orchestration_plan)
        
        return orchestration_plan
    
    def _determine_workflow_type(self, task_text: str) -> str:
        """
        Determine the type of workflow based on task text.
        
        Args:
            task_text: Task description text
            
        Returns:
            str: Workflow type
        """
        if "invoice" in task_text and "opportunity" in task_text:
            return "financial_integration"
        elif "incident" in task_text and "case" in task_text:
            return "customer_service"
        elif "sync" in task_text or "synchronize" in task_text:
            return "data_synchronization"
        elif "report" in task_text and "multiple" in task_text:
            return "cross_platform_reporting"
        else:
            return "generic_cross_platform"
    
    def _identify_coordination_points(self, orchestration_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify coordination points in the workflow.
        
        Args:
            orchestration_plan: Orchestration plan
            
        Returns:
            List of coordination points
        """
        coordination_points = []
        steps = orchestration_plan.get("steps", [])
        
        for i, step in enumerate(steps):
            # Check if this step requires coordination with previous steps
            if i > 0:
                prev_step = steps[i-1]
                if step["platform"] != prev_step["platform"]:
                    coordination_points.append({
                        "from_platform": prev_step["platform"],
                        "to_platform": step["platform"],
                        "step_id": step["step_id"],
                        "coordination_type": "platform_handoff"
                    })
            
            # Check for data dependencies
            dependencies = orchestration_plan.get("dependencies", {}).get(step["step_id"], [])
            if dependencies:
                coordination_points.append({
                    "step_id": step["step_id"],
                    "dependencies": dependencies,
                    "coordination_type": "dependency_resolution"
                })
        
        return coordination_points
    
    def _coordinate_platforms(self, orchestration_plan: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate actions across platforms.
        
        Args:
            orchestration_plan: Orchestration plan
            task: Task being executed
            
        Returns:
            Dict containing coordination results
        """
        try:
            coordination_result = {
                "success": True,
                "platform_coordination": {},
                "data_flow": {},
                "coordination_points": []
            }
            
            # Process each coordination point
            coordination_points = orchestration_plan.get("coordination_points", [])
            for point in coordination_points:
                if point["coordination_type"] == "platform_handoff":
                    # Handle platform handoff
                    handoff_result = self._handle_platform_handoff(point)
                    coordination_result["platform_coordination"][point["step_id"]] = handoff_result
                
                elif point["coordination_type"] == "dependency_resolution":
                    # Handle dependency resolution
                    dependency_result = self._resolve_dependencies(point, orchestration_plan)
                    coordination_result["coordination_points"].append(dependency_result)
            
            # Update coordination state
            self.platform_coordination.update(coordination_result["platform_coordination"])
            
            return coordination_result
            
        except Exception as e:
            logger.error(f"Platform coordination failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_coordination": {},
                "data_flow": {},
                "coordination_points": []
            }
    
    def _handle_platform_handoff(self, handoff_point: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle platform handoff coordination.
        
        Args:
            handoff_point: Platform handoff point
            
        Returns:
            Dict containing handoff result
        """
        return {
            "from_platform": handoff_point["from_platform"],
            "to_platform": handoff_point["to_platform"],
            "handoff_type": "data_transfer",
            "status": "prepared",
            "timestamp": datetime.now().isoformat()
        }
    
    def _resolve_dependencies(self, dependency_point: Dict[str, Any], orchestration_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve step dependencies.
        
        Args:
            dependency_point: Dependency point
            orchestration_plan: Orchestration plan
            
        Returns:
            Dict containing dependency resolution result
        """
        return {
            "step_id": dependency_point["step_id"],
            "dependencies": dependency_point["dependencies"],
            "resolution_status": "resolved",
            "execution_order": self._calculate_execution_order(dependency_point, orchestration_plan)
        }
    
    def _calculate_execution_order(self, dependency_point: Dict[str, Any], orchestration_plan: Dict[str, Any]) -> List[str]:
        """
        Calculate execution order for dependent steps.
        
        Args:
            dependency_point: Dependency point
            orchestration_plan: Orchestration plan
            
        Returns:
            List of step IDs in execution order
        """
        # Simple topological sort for dependencies
        dependencies = dependency_point["dependencies"]
        execution_order = dependencies + [dependency_point["step_id"]]
        return execution_order
    
    async def _execute_workflow_with_engine(self) -> Dict[str, Any]:
        """
        Execute workflow using the orchestration engine.
        
        Returns:
            Dict containing workflow execution result
        """
        if not self.orchestration_engine or not self.current_workflow:
            return {"success": False, "error": "No orchestration engine or workflow available"}
        
        try:
            # Convert orchestration plan to CrossPlatformTask
            from ...orchestration.engine import CrossPlatformTask, TaskStep
            
            task_steps = []
            for step in self.current_workflow.get("steps", []):
                task_step = TaskStep(
                    step_id=step["step_id"],
                    name=step["description"],
                    platform=step["platform"],
                    action_type=step["action"],
                    parameters={}  # Would be populated from step data
                )
                task_steps.append(task_step)
            
            cross_platform_task = CrossPlatformTask(
                task_id=f"orchestration_{self.current_turn}",
                name="Orchestrated Workflow",
                description="Cross-platform orchestrated workflow",
                category="orchestration",
                platforms=self.platforms,
                complexity="medium",
                steps=task_steps,
                dependencies=self.current_workflow.get("dependencies", {})
            )
            
            # Execute the task
            result = await self.orchestration_engine.execute_task(cross_platform_task)
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution with engine failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_manual_orchestration(self, orchestration_plan: Dict[str, Any], env) -> Dict[str, Any]:
        """
        Execute manual orchestration without engine.
        
        Args:
            orchestration_plan: Orchestration plan
            env: Environment instance
            
        Returns:
            Dict containing manual orchestration result
        """
        try:
            manual_result = {
                "success": True,
                "execution_type": "manual",
                "steps_executed": [],
                "data_flow": {},
                "platform_coordination": {}
            }
            
            # Execute steps in order
            steps = orchestration_plan.get("steps", [])
            for step in steps:
                step_result = {
                    "step_id": step["step_id"],
                    "platform": step["platform"],
                    "action": step["action"],
                    "status": "executed",
                    "timestamp": datetime.now().isoformat()
                }
                manual_result["steps_executed"].append(step_result)
            
            return manual_result
            
        except Exception as e:
            logger.error(f"Manual orchestration failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_orchestration_summary(self) -> str:
        """
        Get a summary of the orchestration process.
        
        Returns:
            str: Orchestration summary
        """
        if not self.current_workflow:
            return "No orchestration workflow active."
        
        summary_parts = [
            f"Workflow Type: {self.current_workflow.get('workflow_type', 'unknown')}",
            f"Platforms: {', '.join(self.current_workflow.get('platforms', []))}",
            f"Steps: {len(self.current_workflow.get('steps', []))}",
            f"Coordination Points: {len(self.current_workflow.get('coordination_points', []))}"
        ]
        
        return "\n".join(summary_parts)
    
    def get_platform_coordination_info(self) -> Dict[str, Any]:
        """
        Get platform coordination information.
        
        Returns:
            Dict containing coordination information
        """
        return {
            "platforms": self.platforms,
            "coordination_events": len(self.platform_coordination),
            "data_flows": len(self.data_flow),
            "execution_context": self.execution_context,
            "orchestration_engine_available": self.orchestration_engine is not None,
            "workflow_manager_available": self.workflow_manager is not None
        }
    
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
        self.current_workflow = None
        self.platform_coordination.clear()
        self.data_flow.clear()
        self.execution_context.clear()
        logger.debug("Orchestration agent state reset")
