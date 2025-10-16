"""
Platform Factory and Registry

This module provides factory classes for creating and managing platform instances.
"""

import logging
from typing import Dict, List, Optional, Type
from .base.platform import BasePlatform, PlatformCredentials, PlatformType
from .base.exceptions import PlatformError, ConfigurationError

logger = logging.getLogger(__name__)


class PlatformFactory:
    """Factory class for creating platform instances."""
    
    _platform_classes: Dict[str, Type[BasePlatform]] = {}
    
    @classmethod
    def _register_default_platforms(cls):
        """Register default platform implementations."""
        try:
            from .salesforce.connector import SalesforceConnector
            cls.register_platform("salesforce", SalesforceConnector)
        except ImportError:
            logger.warning("Salesforce connector not available")
        
        try:
            from .servicenow.connector import ServiceNowConnector
            cls.register_platform("servicenow", ServiceNowConnector)
        except ImportError:
            logger.warning("ServiceNow connector not available")
        
        # Register other platforms as they become available
        try:
            from .netsuite.connector import NetSuiteConnector
            cls.register_platform("netsuite", NetSuiteConnector)
        except ImportError:
            logger.warning("NetSuite connector not available")
        
        try:
            from .quickbooks.connector import QuickBooksConnector
            cls.register_platform("quickbooks", QuickBooksConnector)
        except ImportError:
            logger.warning("QuickBooks connector not available")
    
    @classmethod
    def create_platform(cls, platform_name: str, credentials: PlatformCredentials) -> BasePlatform:
        """
        Create a platform instance.
        
        Args:
            platform_name: Name of the platform to create
            credentials: Platform credentials
            
        Returns:
            BasePlatform: Platform instance
            
        Raises:
            ConfigurationError: If platform is not supported or creation fails
        """
        platform_name = platform_name.lower()
        
        # Register default platforms if not already registered
        if not cls._platform_classes:
            cls._register_default_platforms()
        
        if platform_name not in cls._platform_classes:
            raise ConfigurationError(
                f"Platform '{platform_name}' is not supported. "
                f"Supported platforms: {list(cls._platform_classes.keys())}"
            )
        
        try:
            platform_class = cls._platform_classes[platform_name]
            platform_type = PlatformType(platform_name)
            
            platform = platform_class(credentials, platform_type)
            logger.info(f"Created {platform_name} platform instance")
            
            return platform
            
        except Exception as e:
            logger.error(f"Failed to create {platform_name} platform: {e}")
            raise ConfigurationError(f"Failed to create {platform_name} platform: {e}")
    
    @classmethod
    def register_platform(cls, name: str, platform_class: Type[BasePlatform]):
        """
        Register a platform class.
        
        Args:
            name: Platform name
            platform_class: Platform class to register
        """
        if not issubclass(platform_class, BasePlatform):
            raise ConfigurationError(f"Platform class must inherit from BasePlatform")
        
        cls._platform_classes[name.lower()] = platform_class
        logger.info(f"Registered platform: {name}")
    
    @classmethod
    def get_supported_platforms(cls) -> List[str]:
        """
        Get list of supported platform names.
        
        Returns:
            List of supported platform names
        """
        return list(cls._platform_classes.keys())
    
    @classmethod
    def is_platform_supported(cls, platform_name: str) -> bool:
        """
        Check if a platform is supported.
        
        Args:
            platform_name: Name of the platform to check
            
        Returns:
            bool: True if platform is supported, False otherwise
        """
        return platform_name.lower() in cls._platform_classes


class PlatformRegistry:
    """Registry for managing active platform connections."""
    
    def __init__(self):
        """Initialize the platform registry."""
        self._platforms: Dict[str, BasePlatform] = {}
        self._credentials: Dict[str, PlatformCredentials] = {}
    
    async def register_platform(self, name: str, credentials: PlatformCredentials) -> bool:
        """
        Register and connect to a platform.
        
        Args:
            name: Platform name
            credentials: Platform credentials
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Create platform instance
            platform = PlatformFactory.create_platform(name, credentials)
            
            # Validate credentials
            if not await platform.validate_credentials():
                logger.error(f"Invalid credentials for {name}")
                return False
            
            # Connect to platform
            if not await platform.connect():
                logger.error(f"Failed to connect to {name}")
                return False
            
            # Store platform and credentials
            self._platforms[name.lower()] = platform
            self._credentials[name.lower()] = credentials
            
            logger.info(f"Successfully registered platform: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register platform {name}: {e}")
            return False
    
    async def get_platform(self, name: str) -> Optional[BasePlatform]:
        """
        Get a registered platform instance.
        
        Args:
            name: Platform name
            
        Returns:
            BasePlatform: Platform instance if found, None otherwise
        """
        return self._platforms.get(name.lower())
    
    async def unregister_platform(self, name: str) -> bool:
        """
        Unregister and disconnect from a platform.
        
        Args:
            name: Platform name
            
        Returns:
            bool: True if unregistration successful, False otherwise
        """
        platform_name = name.lower()
        
        if platform_name not in self._platforms:
            logger.warning(f"Platform {name} is not registered")
            return False
        
        try:
            platform = self._platforms[platform_name]
            
            # Disconnect from platform
            await platform.disconnect()
            
            # Remove from registry
            del self._platforms[platform_name]
            del self._credentials[platform_name]
            
            logger.info(f"Successfully unregistered platform: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister platform {name}: {e}")
            return False
    
    async def health_check_all(self) -> Dict[str, Dict[str, any]]:
        """
        Perform health check on all registered platforms.
        
        Returns:
            Dict containing health check results for all platforms
        """
        health_results = {}
        
        for name, platform in self._platforms.items():
            try:
                health_result = await platform.health_check()
                health_results[name] = health_result
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                health_results[name] = {
                    "healthy": False,
                    "status": "error",
                    "error": str(e)
                }
        
        return health_results
    
    async def disconnect_all(self):
        """Disconnect from all registered platforms."""
        for name, platform in self._platforms.items():
            try:
                await platform.disconnect()
                logger.info(f"Disconnected from {name}")
            except Exception as e:
                logger.error(f"Failed to disconnect from {name}: {e}")
        
        self._platforms.clear()
        self._credentials.clear()
        logger.info("Disconnected from all platforms")
    
    def get_registered_platforms(self) -> List[str]:
        """
        Get list of registered platform names.
        
        Returns:
            List of registered platform names
        """
        return list(self._platforms.keys())
    
    def is_platform_registered(self, name: str) -> bool:
        """
        Check if a platform is registered.
        
        Args:
            name: Platform name to check
            
        Returns:
            bool: True if platform is registered, False otherwise
        """
        return name.lower() in self._platforms
    
    def get_platform_count(self) -> int:
        """
        Get number of registered platforms.
        
        Returns:
            int: Number of registered platforms
        """
        return len(self._platforms)
    
    def get_platform_info(self, name: str) -> Optional[Dict[str, any]]:
        """
        Get information about a registered platform.
        
        Args:
            name: Platform name
            
        Returns:
            Dict containing platform information if found, None otherwise
        """
        platform = self._platforms.get(name.lower())
        if platform:
            return platform.get_platform_info()
        return None
    
    def get_all_platform_info(self) -> Dict[str, Dict[str, any]]:
        """
        Get information about all registered platforms.
        
        Returns:
            Dict containing platform information for all registered platforms
        """
        return {
            name: platform.get_platform_info()
            for name, platform in self._platforms.items()
        }
