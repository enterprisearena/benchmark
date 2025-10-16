"""
EnterpriseArena: Multi-Platform Enterprise Software Benchmark

A comprehensive benchmark framework for evaluating LLM agents across multiple
enterprise software platforms, supporting both single-platform and cross-platform workflows.
"""

__version__ = "0.1.0"
__author__ = "EnterpriseArena Team"
__email__ = "contact@enterprisearena.org"

# Import main components
from .data.assets import (
    ALL_TASKS,
    ALL_SINGLE_PLATFORM_TASKS,
    ALL_CROSS_PLATFORM_TASKS,
    SINGLE_PLATFORM_TASKS,
    CROSS_PLATFORM_TASKS,
    get_tasks_by_platform,
    get_tasks_by_category,
    get_all_tasks,
    get_task_by_id,
    get_platforms_for_task
)

# Import platform components
from .platforms.factory import PlatformFactory, PlatformRegistry
from .platforms.base.platform import BasePlatform, PlatformCredentials, QueryResult, ActionResult
from .platforms.salesforce.connector import SalesforceConnector
from .platforms.servicenow.connector import ServiceNowConnector
from .platforms.netsuite.connector import NetSuiteConnector
from .platforms.quickbooks.connector import QuickBooksConnector

# Import agent components
from .agents.base.agent import BaseAgent, AgentResult, AgentState
from .agents.base.chat_agent import ChatAgent
from .agents.base.tool_agent import ToolCallAgent
from .agents.single_platform.react_agent import ReActAgent
from .agents.single_platform.tool_call_agent import SinglePlatformToolCallAgent
from .agents.cross_platform.orchestration_agent import OrchestrationAgent

# Import environment components
from .environments.base.environment import BaseEnvironment, EnvironmentResult, EnvironmentState
from .environments.base.single_platform_env import SinglePlatformEnvironment
from .environments.base.cross_platform_env import CrossPlatformEnvironment

# Import orchestration components
from .orchestration.engine import OrchestrationEngine, CrossPlatformTask, TaskStep

# Import evaluation components
from .evaluation.evaluators.single_platform_evaluator import SinglePlatformEvaluator

# Import configuration components
from .config.config_loader import PlatformConfigLoader, TaskConfigLoader, AgentConfigLoader

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Data assets
    "ALL_TASKS",
    "ALL_SINGLE_PLATFORM_TASKS", 
    "ALL_CROSS_PLATFORM_TASKS",
    "SINGLE_PLATFORM_TASKS",
    "CROSS_PLATFORM_TASKS",
    "get_tasks_by_platform",
    "get_tasks_by_category", 
    "get_all_tasks",
    "get_task_by_id",
    "get_platforms_for_task",
    
    # Platform components
    "PlatformFactory",
    "PlatformRegistry",
    "BasePlatform",
    "PlatformCredentials",
    "QueryResult",
    "ActionResult",
    "SalesforceConnector",
    "ServiceNowConnector",
    "NetSuiteConnector",
    "QuickBooksConnector",
    
    # Agent components
    "BaseAgent",
    "AgentResult",
    "AgentState",
    "ChatAgent",
    "ToolCallAgent",
    "ReActAgent",
    "SinglePlatformToolCallAgent",
    "OrchestrationAgent",
    
    # Environment components
    "BaseEnvironment",
    "EnvironmentResult",
    "EnvironmentState",
    "SinglePlatformEnvironment",
    "CrossPlatformEnvironment",
    
    # Orchestration components
    "OrchestrationEngine",
    "CrossPlatformTask",
    "TaskStep",
    
    # Evaluation components
    "SinglePlatformEvaluator",
    
    # Configuration components
    "PlatformConfigLoader",
    "TaskConfigLoader",
    "AgentConfigLoader",
]
