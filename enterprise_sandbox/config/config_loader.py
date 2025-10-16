"""
Configuration Loader

This module provides configuration loading functionality for EnterpriseArena.
"""

import os
import yaml
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..platforms.base.platform import PlatformCredentials

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Base class for configuration loaders."""
    
    def __init__(self, config_path: str):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self._config_cache: Optional[Dict[str, Any]] = None
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict containing configuration data
        """
        if self._config_cache is not None:
            return self._config_cache
        
        try:
            if not self.config_path.exists():
                logger.warning(f"Configuration file not found: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self._config_cache = config or {}
            logger.debug(f"Loaded configuration from {self.config_path}")
            return self._config_cache
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {self.config_path}: {e}")
            return {}
    
    def reload_config(self):
        """Reload configuration from file."""
        self._config_cache = None
        self._load_config()


class PlatformConfigLoader(ConfigLoader):
    """Configuration loader for platform settings."""
    
    def __init__(self, config_path: str = "configs/platform_config.yaml"):
        """
        Initialize the platform configuration loader.
        
        Args:
            config_path: Path to platform configuration file
        """
        super().__init__(config_path)
    
    def get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific platform.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            Dict containing platform configuration
        """
        config = self._load_config()
        platforms = config.get("platforms", {})
        return platforms.get(platform_name, {})
    
    def create_credentials(self, platform_name: str) -> PlatformCredentials:
        """
        Create platform credentials from configuration.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            PlatformCredentials object
        """
        platform_config = self.get_platform_config(platform_name)
        credentials_config = platform_config.get("credentials", {})
        
        # Handle environment variable substitution
        credentials = {}
        for key, value in credentials_config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                credentials[key] = os.getenv(env_var, value)
            else:
                credentials[key] = value
        
        return PlatformCredentials(**credentials)
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of supported platforms from configuration.
        
        Returns:
            List of platform names
        """
        config = self._load_config()
        return list(config.get("platforms", {}).keys())
    
    def get_platform_environment(self, platform_name: str) -> str:
        """
        Get environment setting for a platform.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            str: Environment setting (e.g., 'production', 'sandbox')
        """
        platform_config = self.get_platform_config(platform_name)
        return platform_config.get("environment", "production")
    
    def get_platform_timeout(self, platform_name: str) -> int:
        """
        Get timeout setting for a platform.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            int: Timeout in seconds
        """
        platform_config = self.get_platform_config(platform_name)
        return platform_config.get("timeout_seconds", 300)


class TaskConfigLoader(ConfigLoader):
    """Configuration loader for task settings."""
    
    def __init__(self, config_path: str = "configs/task_config.yaml"):
        """
        Initialize the task configuration loader.
        
        Args:
            config_path: Path to task configuration file
        """
        super().__init__(config_path)
    
    def get_task_config(self, task_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific task type.
        
        Args:
            task_type: Type of task (e.g., 'single_platform', 'cross_platform')
            
        Returns:
            Dict containing task configuration
        """
        config = self._load_config()
        tasks = config.get("tasks", {})
        return tasks.get(task_type, {})
    
    def get_evaluation_config(self) -> Dict[str, Any]:
        """
        Get evaluation configuration.
        
        Returns:
            Dict containing evaluation configuration
        """
        config = self._load_config()
        return config.get("evaluation", {})
    
    def get_timeout_config(self) -> Dict[str, int]:
        """
        Get timeout configuration for different task types.
        
        Returns:
            Dict containing timeout settings
        """
        config = self._load_config()
        return config.get("timeouts", {
            "single_platform": 300,
            "cross_platform": 600,
            "interactive": 1800
        })
    
    def get_retry_config(self) -> Dict[str, int]:
        """
        Get retry configuration for different task types.
        
        Returns:
            Dict containing retry settings
        """
        config = self._load_config()
        return config.get("retries", {
            "max_retries": 3,
            "retry_delay": 1,
            "exponential_backoff": True
        })


class AgentConfigLoader(ConfigLoader):
    """Configuration loader for agent settings."""
    
    def __init__(self, config_path: str = "configs/agent_config.yaml"):
        """
        Initialize the agent configuration loader.
        
        Args:
            config_path: Path to agent configuration file
        """
        super().__init__(config_path)
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent type.
        
        Args:
            agent_type: Type of agent (e.g., 'react', 'tool_call', 'orchestration')
            
        Returns:
            Dict containing agent configuration
        """
        config = self._load_config()
        agents = config.get("agents", {})
        return agents.get(agent_type, {})
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict containing model configuration
        """
        config = self._load_config()
        models = config.get("models", {})
        return models.get(model_name, {})
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider_name: Name of the provider (e.g., 'openai', 'anthropic')
            
        Returns:
            Dict containing provider configuration
        """
        config = self._load_config()
        providers = config.get("providers", {})
        return providers.get(provider_name, {})
    
    def get_default_agent_config(self) -> Dict[str, Any]:
        """
        Get default agent configuration.
        
        Returns:
            Dict containing default agent configuration
        """
        config = self._load_config()
        return config.get("default_agent", {
            "max_turns": 20,
            "timeout_seconds": 300,
            "enable_logging": True,
            "debug_mode": False
        })
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models from configuration.
        
        Returns:
            List of model names
        """
        config = self._load_config()
        return list(config.get("models", {}).keys())
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available providers from configuration.
        
        Returns:
            List of provider names
        """
        config = self._load_config()
        return list(config.get("providers", {}).keys())


class EnvironmentConfigLoader(ConfigLoader):
    """Configuration loader for environment settings."""
    
    def __init__(self, config_path: str = "configs/environment_config.yaml"):
        """
        Initialize the environment configuration loader.
        
        Args:
            config_path: Path to environment configuration file
        """
        super().__init__(config_path)
    
    def get_environment_config(self, environment_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific environment type.
        
        Args:
            environment_type: Type of environment (e.g., 'single_platform', 'cross_platform')
            
        Returns:
            Dict containing environment configuration
        """
        config = self._load_config()
        environments = config.get("environments", {})
        return environments.get(environment_type, {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.
        
        Returns:
            Dict containing logging configuration
        """
        config = self._load_config()
        return config.get("logging", {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/enterprise_arena.log"
        })
    
    def get_performance_config(self) -> Dict[str, Any]:
        """
        Get performance configuration.
        
        Returns:
            Dict containing performance configuration
        """
        config = self._load_config()
        return config.get("performance", {
            "max_concurrent_tasks": 10,
            "connection_pool_size": 5,
            "cache_size": 1000,
            "cache_ttl": 3600
        })


def load_all_configs(config_dir: str = "configs") -> Dict[str, Any]:
    """
    Load all configuration files from a directory.
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        Dict containing all loaded configurations
    """
    config_dir = Path(config_dir)
    
    configs = {}
    
    # Load platform configuration
    platform_config_path = config_dir / "platform_config.yaml"
    if platform_config_path.exists():
        platform_loader = PlatformConfigLoader(str(platform_config_path))
        configs["platforms"] = platform_loader._load_config()
    
    # Load task configuration
    task_config_path = config_dir / "task_config.yaml"
    if task_config_path.exists():
        task_loader = TaskConfigLoader(str(task_config_path))
        configs["tasks"] = task_loader._load_config()
    
    # Load agent configuration
    agent_config_path = config_dir / "agent_config.yaml"
    if agent_config_path.exists():
        agent_loader = AgentConfigLoader(str(agent_config_path))
        configs["agents"] = agent_loader._load_config()
    
    # Load environment configuration
    env_config_path = config_dir / "environment_config.yaml"
    if env_config_path.exists():
        env_loader = EnvironmentConfigLoader(str(env_config_path))
        configs["environments"] = env_loader._load_config()
    
    logger.info(f"Loaded configurations from {config_dir}")
    return configs
