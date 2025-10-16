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

# Import platform components (will be available when implemented)
try:
    from .platforms.factory import PlatformFactory
    from .platforms.base.platform import BasePlatform
except ImportError:
    # Platform components not yet implemented
    pass

# Import agent components (will be available when implemented)
try:
    from .agents.base.agent import BaseAgent
    from .agents.single_platform.react_agent import ReActAgent
    from .agents.cross_platform.orchestration_agent import OrchestrationAgent
except ImportError:
    # Agent components not yet implemented
    pass

# Import environment components (will be available when implemented)
try:
    from .environments.base.environment import BaseEnvironment
    from .environments.single_platform.chat_env import ChatEnvironment
    from .environments.cross_platform.orchestration_env import OrchestrationEnvironment
except ImportError:
    # Environment components not yet implemented
    pass

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
    
    # Platform components (when available)
    "PlatformFactory",
    "BasePlatform",
    
    # Agent components (when available)
    "BaseAgent",
    "ReActAgent", 
    "OrchestrationAgent",
    
    # Environment components (when available)
    "BaseEnvironment",
    "ChatEnvironment",
    "OrchestrationEnvironment",
]
