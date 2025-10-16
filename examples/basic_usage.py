"""
Basic Usage Example for EnterpriseArena

This example demonstrates how to use the core components of EnterpriseArena
for single-platform and cross-platform task execution.
"""

import asyncio
import logging
from enterprise_sandbox import (
    # Platform components
    PlatformFactory, PlatformCredentials, SalesforceConnector,
    
    # Agent components
    ReActAgent,
    
    # Environment components
    SinglePlatformEnvironment,
    
    # Data assets
    get_tasks_by_platform,
    
    # Configuration
    PlatformConfigLoader
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def single_platform_example():
    """Example of single-platform task execution."""
    logger.info("=== Single Platform Example ===")
    
    try:
        # 1. Load platform configuration
        config_loader = PlatformConfigLoader("configs/platform_config.yaml")
        
        # 2. Create platform credentials (you would set these in your environment)
        credentials = PlatformCredentials(
            username="your_username",
            password="your_password", 
            security_token="your_security_token",
            environment="sandbox"
        )
        
        # 3. Create platform connection
        platform = PlatformFactory.create_platform("salesforce", credentials)
        
        # 4. Connect to platform
        connected = await platform.connect()
        if not connected:
            logger.error("Failed to connect to Salesforce")
            return
        
        logger.info("Successfully connected to Salesforce")
        
        # 5. Get tasks for the platform
        tasks = get_tasks_by_platform("salesforce")
        logger.info(f"Found {len(tasks)} Salesforce tasks")
        
        # 6. Create environment
        env = SinglePlatformEnvironment(
            tasks={i: task for i, task in enumerate(tasks[:3])},  # Use first 3 tasks
            platform="salesforce"
        )
        env.set_platform_connection(platform)
        
        # 7. Create agent
        agent = ReActAgent(
            model="gpt-4o",
            schema_obj={},  # Would load actual schema
            max_turns=10
        )
        
        # 8. Execute tasks
        for task_index in range(min(3, len(tasks))):
            logger.info(f"Executing task {task_index}: {tasks[task_index].get('task', 'No description')}")
            
            # Reset environment for new task
            observation, info = env.reset(task_index)
            
            # Execute task with agent
            reward = agent.act(env, task_index)
            
            logger.info(f"Task {task_index} completed with reward: {reward}")
        
        # 9. Disconnect
        await platform.disconnect()
        logger.info("Disconnected from Salesforce")
        
    except Exception as e:
        logger.error(f"Single platform example failed: {e}")


async def cross_platform_example():
    """Example of cross-platform task execution."""
    logger.info("=== Cross Platform Example ===")
    
    try:
        # 1. Create platform connections
        platform_connections = {}
        
        # Salesforce connection
        sf_credentials = PlatformCredentials(
            username="your_sf_username",
            password="your_sf_password",
            security_token="your_sf_token",
            environment="sandbox"
        )
        sf_platform = PlatformFactory.create_platform("salesforce", sf_credentials)
        await sf_platform.connect()
        platform_connections["salesforce"] = sf_platform
        
        # QuickBooks connection (would be implemented)
        # qb_credentials = PlatformCredentials(...)
        # qb_platform = PlatformFactory.create_platform("quickbooks", qb_credentials)
        # await qb_platform.connect()
        # platform_connections["quickbooks"] = qb_platform
        
        logger.info(f"Connected to {len(platform_connections)} platforms")
        
        # 2. Create cross-platform task
        from enterprise_sandbox.orchestration.engine import CrossPlatformTask, TaskStep
        
        task = CrossPlatformTask(
            task_id="invoice_to_opportunity_001",
            name="Invoice to Opportunity Workflow",
            description="Convert QuickBooks invoice to Salesforce opportunity",
            category="financial_integration",
            platforms=["quickbooks", "salesforce"],
            complexity="medium",
            steps=[
                TaskStep(
                    step_id="fetch_invoice",
                    name="Fetch Invoice from QuickBooks",
                    platform="quickbooks",
                    action_type="query",
                    parameters={
                        "query": "SELECT * FROM Invoice WHERE InvoiceNumber = 'INV-2024-001'"
                    }
                ),
                TaskStep(
                    step_id="create_opportunity",
                    name="Create Opportunity in Salesforce",
                    platform="salesforce", 
                    action_type="create",
                    parameters={
                        "object_type": "Opportunity",
                        "data": {
                            "Name": "Invoice Opportunity",
                            "StageName": "Prospecting",
                            "CloseDate": "2024-12-31"
                        }
                    }
                )
            ],
            dependencies={
                "create_opportunity": ["fetch_invoice"]
            }
        )
        
        # 3. Create orchestration engine
        from enterprise_sandbox.orchestration.engine import OrchestrationEngine
        engine = OrchestrationEngine(platform_connections)
        
        # 4. Execute cross-platform task
        logger.info("Executing cross-platform workflow...")
        result = await engine.execute_task(task)
        
        logger.info(f"Cross-platform task completed: {result}")
        
        # 5. Clean up
        for platform in platform_connections.values():
            await platform.disconnect()
        
        logger.info("Disconnected from all platforms")
        
    except Exception as e:
        logger.error(f"Cross platform example failed: {e}")


async def evaluation_example():
    """Example of task evaluation."""
    logger.info("=== Evaluation Example ===")
    
    try:
        from enterprise_sandbox.evaluation.evaluators.single_platform_evaluator import SinglePlatformEvaluator
        
        # 1. Create evaluator
        evaluator = SinglePlatformEvaluator(model="gpt-4o", provider="openai")
        
        # 2. Sample task and result
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
        
        # 3. Evaluate task
        metrics = evaluator.evaluate_task(task, execution_result)
        
        logger.info(f"Evaluation metrics: {metrics}")
        
        # 4. Generate performance report
        agent_results = [execution_result]  # Would be multiple results in practice
        performance = evaluator.evaluate_agent_performance(agent_results)
        
        logger.info(f"Agent performance: {performance}")
        
    except Exception as e:
        logger.error(f"Evaluation example failed: {e}")


async def main():
    """Main function to run all examples."""
    logger.info("Starting EnterpriseArena examples...")
    
    # Note: These examples require actual platform credentials and connections
    # They are provided as templates for how to use the framework
    
    # await single_platform_example()
    # await cross_platform_example()
    await evaluation_example()
    
    logger.info("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
