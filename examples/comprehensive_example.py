"""
Comprehensive EnterpriseArena Example

This example demonstrates the full capabilities of EnterpriseArena including:
- Single-platform task execution with different agent types
- Cross-platform workflow orchestration
- Evaluation and performance analysis
- Configuration management
"""

import asyncio
import logging
import os
from typing import Dict, List, Any
from enterprise_sandbox import (
    # Platform components
    PlatformFactory, PlatformCredentials, PlatformRegistry,
    SalesforceConnector, ServiceNowConnector,
    
    # Agent components
    ReActAgent, SinglePlatformToolCallAgent, OrchestrationAgent,
    
    # Environment components
    SinglePlatformEnvironment, CrossPlatformEnvironment,
    
    # Orchestration components
    OrchestrationEngine, CrossPlatformTask, TaskStep,
    
    # Evaluation components
    SinglePlatformEvaluator,
    
    # Configuration components
    PlatformConfigLoader, TaskConfigLoader, AgentConfigLoader,
    
    # Data assets
    get_tasks_by_platform, get_tasks_by_category
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnterpriseArenaDemo:
    """Comprehensive demonstration of EnterpriseArena capabilities."""
    
    def __init__(self):
        """Initialize the demo."""
        self.platform_registry = PlatformRegistry()
        self.orchestration_engine = None
        self.evaluator = SinglePlatformEvaluator(model="gpt-4o", provider="openai")
        self.results = {}
        
    async def setup_platforms(self):
        """Set up platform connections."""
        logger.info("=== Setting up Platform Connections ===")
        
        # Load configuration
        config_loader = PlatformConfigLoader("configs/platform_config.yaml")
        
        # Set up Salesforce (if credentials available)
        try:
            sf_credentials = PlatformCredentials(
                username=os.getenv("SALESFORCE_USERNAME", "demo_user"),
                password=os.getenv("SALESFORCE_PASSWORD", "demo_pass"),
                security_token=os.getenv("SALESFORCE_SECURITY_TOKEN", "demo_token"),
                environment="sandbox"
            )
            
            await self.platform_registry.register_platform("salesforce", sf_credentials)
            logger.info("✅ Salesforce platform registered")
            
        except Exception as e:
            logger.warning(f"⚠️ Salesforce setup failed: {e}")
        
        # Set up ServiceNow (if credentials available)
        try:
            sn_credentials = PlatformCredentials(
                username=os.getenv("SERVICENOW_USERNAME", "demo_user"),
                password=os.getenv("SERVICENOW_PASSWORD", "demo_pass"),
                instance_url=os.getenv("SERVICENOW_INSTANCE_URL", "demo.service-now.com"),
                environment="sandbox"
            )
            
            await self.platform_registry.register_platform("servicenow", sn_credentials)
            logger.info("✅ ServiceNow platform registered")
            
        except Exception as e:
            logger.warning(f"⚠️ ServiceNow setup failed: {e}")
        
        # Set up orchestration engine
        platform_connections = {}
        for platform_name in ["salesforce", "servicenow"]:
            platform = await self.platform_registry.get_platform(platform_name)
            if platform:
                platform_connections[platform_name] = platform
        
        if platform_connections:
            self.orchestration_engine = OrchestrationEngine(platform_connections)
            logger.info(f"✅ Orchestration engine initialized with {len(platform_connections)} platforms")
    
    async def demo_single_platform_react_agent(self):
        """Demonstrate single-platform ReAct agent."""
        logger.info("\n=== Single-Platform ReAct Agent Demo ===")
        
        try:
            # Get Salesforce tasks
            tasks = get_tasks_by_platform("salesforce")
            if not tasks:
                logger.warning("No Salesforce tasks available")
                return
            
            # Get platform connection
            platform = await self.platform_registry.get_platform("salesforce")
            if not platform:
                logger.warning("Salesforce platform not available")
                return
            
            # Create environment
            env = SinglePlatformEnvironment(
                tasks={i: task for i, task in enumerate(tasks[:2])},  # Use first 2 tasks
                platform="salesforce"
            )
            env.set_platform_connection(platform)
            
            # Create ReAct agent
            agent = ReActAgent(
                model="gpt-4o",
                schema_obj={},  # Would load actual schema
                max_turns=10,
                strategy="react"
            )
            
            # Execute tasks
            task_results = []
            for task_index in range(min(2, len(tasks))):
                logger.info(f"Executing task {task_index}: {tasks[task_index].get('task', 'No description')}")
                
                # Reset environment for new task
                observation, info = env.reset(task_index)
                
                # Execute with agent
                reward = agent.act(env, task_index)
                task_results.append({
                    "task_index": task_index,
                    "reward": reward,
                    "success": reward > 0,
                    "execution_time": agent.total_execution_time,
                    "steps_taken": agent.total_steps
                })
                
                logger.info(f"Task {task_index} completed with reward: {reward}")
            
            self.results["react_agent"] = task_results
            logger.info("✅ ReAct agent demo completed")
            
        except Exception as e:
            logger.error(f"❌ ReAct agent demo failed: {e}")
    
    async def demo_single_platform_tool_agent(self):
        """Demonstrate single-platform tool-calling agent."""
        logger.info("\n=== Single-Platform Tool-Calling Agent Demo ===")
        
        try:
            # Get ServiceNow tasks
            tasks = get_tasks_by_platform("servicenow")
            if not tasks:
                logger.warning("No ServiceNow tasks available")
                return
            
            # Get platform connection
            platform = await self.platform_registry.get_platform("servicenow")
            if not platform:
                logger.warning("ServiceNow platform not available")
                return
            
            # Create environment
            env = SinglePlatformEnvironment(
                tasks={i: task for i, task in enumerate(tasks[:2])},  # Use first 2 tasks
                platform="servicenow"
            )
            env.set_platform_connection(platform)
            
            # Create tool-calling agent
            agent = SinglePlatformToolCallAgent(
                model="gpt-4o",
                schema_obj={},  # Would load actual schema
                max_turns=15,
                max_tool_calls=10
            )
            
            # Register some tools
            agent.register_tool(
                "search_incidents",
                lambda criteria: platform.search_records("incident", criteria),
                "Search for incidents with given criteria"
            )
            
            agent.register_tool(
                "create_incident",
                lambda data: platform.create_record("incident", data),
                "Create a new incident"
            )
            
            # Execute tasks
            task_results = []
            for task_index in range(min(2, len(tasks))):
                logger.info(f"Executing task {task_index}: {tasks[task_index].get('task', 'No description')}")
                
                # Reset environment for new task
                observation, info = env.reset(task_index)
                
                # Execute with agent
                reward = agent.act(env, task_index)
                task_results.append({
                    "task_index": task_index,
                    "reward": reward,
                    "success": reward > 0,
                    "execution_time": agent.total_execution_time,
                    "steps_taken": agent.total_steps,
                    "tool_calls_made": agent.tool_calls_made
                })
                
                logger.info(f"Task {task_index} completed with reward: {reward}")
            
            self.results["tool_agent"] = task_results
            logger.info("✅ Tool-calling agent demo completed")
            
        except Exception as e:
            logger.error(f"❌ Tool-calling agent demo failed: {e}")
    
    async def demo_cross_platform_orchestration(self):
        """Demonstrate cross-platform orchestration."""
        logger.info("\n=== Cross-Platform Orchestration Demo ===")
        
        try:
            if not self.orchestration_engine:
                logger.warning("Orchestration engine not available")
                return
            
            # Create cross-platform task
            task = CrossPlatformTask(
                task_id="demo_workflow_001",
                name="Incident to Case Workflow",
                description="Convert ServiceNow incident to Salesforce case",
                category="customer_service",
                platforms=["servicenow", "salesforce"],
                complexity="medium",
                steps=[
                    TaskStep(
                        step_id="fetch_incident",
                        name="Fetch Incident from ServiceNow",
                        platform="servicenow",
                        action_type="query",
                        parameters={
                            "query": "incident",
                            "criteria": {"state": "New"}
                        }
                    ),
                    TaskStep(
                        step_id="create_case",
                        name="Create Case in Salesforce",
                        platform="salesforce",
                        action_type="create",
                        parameters={
                            "object_type": "Case",
                            "data": {
                                "Subject": "Converted from ServiceNow",
                                "Status": "New",
                                "Origin": "ServiceNow"
                            }
                        }
                    )
                ],
                dependencies={
                    "create_case": ["fetch_incident"]
                }
            )
            
            # Execute cross-platform workflow
            logger.info("Executing cross-platform workflow...")
            result = await self.orchestration_engine.execute_task(task)
            
            self.results["orchestration"] = result
            logger.info(f"✅ Cross-platform orchestration completed: {result.get('status', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Cross-platform orchestration demo failed: {e}")
    
    async def demo_evaluation(self):
        """Demonstrate evaluation capabilities."""
        logger.info("\n=== Evaluation Demo ===")
        
        try:
            # Sample task and execution result
            task = {
                "task": "Find all leads created in the last 30 days",
                "answer": ["Lead1", "Lead2", "Lead3"],
                "reward_metric": "exact_match"
            }
            
            execution_result = {
                "success": True,
                "data": ["Lead1", "Lead2", "Lead3"],
                "execution_time": 2.5,
                "steps_taken": 3
            }
            
            # Evaluate task
            metrics = self.evaluator.evaluate_task(task, execution_result)
            logger.info(f"Evaluation metrics: {metrics}")
            
            # Generate performance report
            agent_results = [execution_result]
            performance = self.evaluator.evaluate_agent_performance(agent_results)
            logger.info(f"Agent performance: {performance}")
            
            self.results["evaluation"] = {
                "metrics": metrics,
                "performance": performance
            }
            
            logger.info("✅ Evaluation demo completed")
            
        except Exception as e:
            logger.error(f"❌ Evaluation demo failed: {e}")
    
    async def demo_configuration_management(self):
        """Demonstrate configuration management."""
        logger.info("\n=== Configuration Management Demo ===")
        
        try:
            # Load configurations
            platform_config = PlatformConfigLoader("configs/platform_config.yaml")
            task_config = TaskConfigLoader("configs/task_config.yaml")
            agent_config = AgentConfigLoader("configs/agent_config.yaml")
            
            # Get configuration examples
            supported_platforms = platform_config.get_supported_platforms()
            logger.info(f"Supported platforms: {supported_platforms}")
            
            task_timeouts = task_config.get_timeout_config()
            logger.info(f"Task timeouts: {task_timeouts}")
            
            available_models = agent_config.get_available_models()
            logger.info(f"Available models: {available_models}")
            
            self.results["configuration"] = {
                "supported_platforms": supported_platforms,
                "task_timeouts": task_timeouts,
                "available_models": available_models
            }
            
            logger.info("✅ Configuration management demo completed")
            
        except Exception as e:
            logger.error(f"❌ Configuration management demo failed: {e}")
    
    def generate_summary_report(self):
        """Generate a summary report of all demos."""
        logger.info("\n" + "="*60)
        logger.info("ENTERPRISE ARENA DEMO SUMMARY REPORT")
        logger.info("="*60)
        
        # ReAct Agent Results
        if "react_agent" in self.results:
            react_results = self.results["react_agent"]
            total_tasks = len(react_results)
            successful_tasks = sum(1 for r in react_results if r["success"])
            avg_reward = sum(r["reward"] for r in react_results) / total_tasks if total_tasks > 0 else 0
            
            logger.info(f"\nReAct Agent Results:")
            logger.info(f"  - Tasks executed: {total_tasks}")
            logger.info(f"  - Successful tasks: {successful_tasks}")
            logger.info(f"  - Success rate: {successful_tasks/total_tasks*100:.1f}%")
            logger.info(f"  - Average reward: {avg_reward:.2f}")
        
        # Tool-Calling Agent Results
        if "tool_agent" in self.results:
            tool_results = self.results["tool_agent"]
            total_tasks = len(tool_results)
            successful_tasks = sum(1 for r in tool_results if r["success"])
            total_tool_calls = sum(r.get("tool_calls_made", 0) for r in tool_results)
            
            logger.info(f"\nTool-Calling Agent Results:")
            logger.info(f"  - Tasks executed: {total_tasks}")
            logger.info(f"  - Successful tasks: {successful_tasks}")
            logger.info(f"  - Success rate: {successful_tasks/total_tasks*100:.1f}%")
            logger.info(f"  - Total tool calls: {total_tool_calls}")
        
        # Orchestration Results
        if "orchestration" in self.results:
            orchestration_result = self.results["orchestration"]
            logger.info(f"\nCross-Platform Orchestration Results:")
            logger.info(f"  - Status: {orchestration_result.get('status', 'unknown')}")
            logger.info(f"  - Execution time: {orchestration_result.get('execution_time', 0):.2f}s")
            logger.info(f"  - Steps completed: {orchestration_result.get('steps_completed', 0)}")
        
        # Evaluation Results
        if "evaluation" in self.results:
            eval_results = self.results["evaluation"]
            metrics = eval_results["metrics"]
            performance = eval_results["performance"]
            
            logger.info(f"\nEvaluation Results:")
            logger.info(f"  - Overall score: {metrics.get('overall_score', 0):.2f}")
            logger.info(f"  - Accuracy: {metrics.get('accuracy', 0):.2f}")
            logger.info(f"  - Efficiency: {metrics.get('efficiency', 0):.2f}")
            logger.info(f"  - Error handling: {metrics.get('error_handling', 0):.2f}")
            logger.info(f"  - Performance grade: {performance.get('performance_grade', 'N/A')}")
        
        # Configuration Results
        if "configuration" in self.results:
            config_results = self.results["configuration"]
            logger.info(f"\nConfiguration Management Results:")
            logger.info(f"  - Supported platforms: {len(config_results.get('supported_platforms', []))}")
            logger.info(f"  - Available models: {len(config_results.get('available_models', []))}")
        
        logger.info("\n" + "="*60)
        logger.info("DEMO COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
    
    async def run_all_demos(self):
        """Run all demonstration scenarios."""
        logger.info("Starting EnterpriseArena Comprehensive Demo...")
        
        try:
            # Setup
            await self.setup_platforms()
            
            # Run demos
            await self.demo_single_platform_react_agent()
            await self.demo_single_platform_tool_agent()
            await self.demo_cross_platform_orchestration()
            await self.demo_evaluation()
            await self.demo_configuration_management()
            
            # Generate summary
            self.generate_summary_report()
            
        except Exception as e:
            logger.error(f"Demo execution failed: {e}")
        finally:
            # Cleanup
            await self.platform_registry.disconnect_all()
            logger.info("Platform connections closed")


async def main():
    """Main function to run the comprehensive demo."""
    demo = EnterpriseArenaDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())
