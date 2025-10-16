"""
Base Platform Implementation

This module defines the abstract base class and data structures for all platform
implementations in EnterpriseArena.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Enumeration of supported platform types."""
    SALESFORCE = "salesforce"
    SERVICENOW = "servicenow"
    NETSUITE = "netsuite"
    QUICKBOOKS = "quickbooks"


class ActionType(Enum):
    """Enumeration of supported action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    QUERY = "query"
    EXECUTE = "execute"


@dataclass
class PlatformCredentials:
    """Data class for platform credentials."""
    username: str
    password: str
    api_key: Optional[str] = None
    security_token: Optional[str] = None
    instance_url: Optional[str] = None
    environment: str = "production"
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    company_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


@dataclass
class QueryResult:
    """Data class for query execution results."""
    data: List[Dict[str, Any]]
    total_count: int
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0
    query_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ActionResult:
    """Data class for action execution results."""
    success: bool
    record_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    action_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BasePlatform(ABC):
    """
    Abstract base class for all platform implementations.
    
    This class defines the interface that all platform connectors must implement
    to ensure consistent behavior across different enterprise software platforms.
    """
    
    def __init__(self, credentials: PlatformCredentials, platform_type: PlatformType):
        """
        Initialize the platform connector.
        
        Args:
            credentials: Platform-specific credentials
            platform_type: Type of platform being connected to
        """
        self.credentials = credentials
        self.platform_type = platform_type
        self.connected = False
        self.connection_time = None
        self._session = None
        self._rate_limiter = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the platform.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the platform.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate platform credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_schema(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get platform schema information.
        
        Args:
            object_type: Optional specific object type to get schema for
            
        Returns:
            Dict containing schema information
        """
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """
        Execute a query against the platform.
        
        Args:
            query: Query string to execute
            parameters: Optional parameters for the query
            
        Returns:
            QueryResult containing query results
        """
        pass
    
    @abstractmethod
    async def execute_action(self, action_type: ActionType, parameters: Dict[str, Any]) -> ActionResult:
        """
        Execute an action against the platform.
        
        Args:
            action_type: Type of action to execute
            parameters: Parameters for the action
            
        Returns:
            ActionResult containing action results
        """
        pass
    
    @abstractmethod
    async def search_records(self, object_type: str, criteria: Dict[str, Any]) -> QueryResult:
        """
        Search for records in the platform.
        
        Args:
            object_type: Type of object to search for
            criteria: Search criteria
            
        Returns:
            QueryResult containing search results
        """
        pass
    
    @abstractmethod
    async def create_record(self, object_type: str, data: Dict[str, Any]) -> ActionResult:
        """
        Create a new record in the platform.
        
        Args:
            object_type: Type of object to create
            data: Data for the new record
            
        Returns:
            ActionResult containing creation results
        """
        pass
    
    @abstractmethod
    async def update_record(self, object_type: str, record_id: str, data: Dict[str, Any]) -> ActionResult:
        """
        Update an existing record in the platform.
        
        Args:
            object_type: Type of object to update
            record_id: ID of the record to update
            data: Updated data for the record
            
        Returns:
            ActionResult containing update results
        """
        pass
    
    @abstractmethod
    async def delete_record(self, object_type: str, record_id: str) -> ActionResult:
        """
        Delete a record from the platform.
        
        Args:
            object_type: Type of object to delete
            record_id: ID of the record to delete
            
        Returns:
            ActionResult containing deletion results
        """
        pass
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get information about the platform.
        
        Returns:
            Dict containing platform information
        """
        return {
            "platform_type": self.platform_type.value,
            "connected": self.connected,
            "connection_time": self.connection_time,
            "environment": self.credentials.environment,
            "instance_url": self.credentials.instance_url
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the platform connection.
        
        Returns:
            Dict containing health check results
        """
        start_time = datetime.now()
        
        try:
            # Basic connectivity check
            if not self.connected:
                return {
                    "healthy": False,
                    "status": "disconnected",
                    "error": "Platform not connected",
                    "response_time": 0.0
                }
            
            # Platform-specific health check
            health_result = await self._perform_health_check()
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "healthy": health_result.get("healthy", True),
                "status": "connected" if health_result.get("healthy", True) else "unhealthy",
                "response_time": response_time,
                "details": health_result
            }
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Health check failed for {self.platform_type.value}: {e}")
            
            return {
                "healthy": False,
                "status": "error",
                "error": str(e),
                "response_time": response_time
            }
    
    @abstractmethod
    async def _perform_health_check(self) -> Dict[str, Any]:
        """
        Platform-specific health check implementation.
        
        Returns:
            Dict containing platform-specific health check results
        """
        pass
    
    async def _handle_rate_limit(self, retry_after: int = None):
        """
        Handle rate limiting by waiting for the specified time.
        
        Args:
            retry_after: Seconds to wait before retrying
        """
        if retry_after:
            logger.warning(f"Rate limit hit, waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
        else:
            # Default exponential backoff
            await asyncio.sleep(1)
    
    def _validate_connection(self):
        """
        Validate that the platform is connected.
        
        Raises:
            PlatformConnectionError: If platform is not connected
        """
        if not self.connected:
            raise PlatformConnectionError(f"Platform {self.platform_type.value} is not connected")
    
    def _log_operation(self, operation: str, start_time: datetime, success: bool, error: str = None):
        """
        Log platform operations for monitoring and debugging.
        
        Args:
            operation: Name of the operation
            start_time: When the operation started
            success: Whether the operation was successful
            error: Error message if operation failed
        """
        duration = (datetime.now() - start_time).total_seconds()
        
        if success:
            logger.info(f"{self.platform_type.value} {operation} completed in {duration:.2f}s")
        else:
            logger.error(f"{self.platform_type.value} {operation} failed after {duration:.2f}s: {error}")
    
    def __str__(self) -> str:
        """String representation of the platform."""
        return f"{self.platform_type.value.title()}Platform(connected={self.connected})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the platform."""
        return (f"{self.__class__.__name__}("
                f"platform_type={self.platform_type.value}, "
                f"connected={self.connected}, "
                f"environment={self.credentials.environment})")
