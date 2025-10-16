"""
ServiceNow Platform Connector

This module implements the ServiceNow platform connector for EnterpriseArena.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp
import json
import base64

from ..base.platform import (
    BasePlatform, PlatformCredentials, QueryResult, ActionResult, 
    PlatformType, ActionType
)
from ..base.exceptions import (
    PlatformConnectionError, AuthenticationError, RateLimitError,
    QueryError, ActionError, ValidationError
)
from ..base.utils import PlatformUtils

logger = logging.getLogger(__name__)


class ServiceNowConnector(BasePlatform):
    """
    ServiceNow platform connector implementation.
    
    This class provides the concrete implementation for connecting to and
    interacting with ServiceNow using the REST API.
    """
    
    def __init__(self, credentials: PlatformCredentials, platform_type: PlatformType):
        """
        Initialize ServiceNow connector.
        
        Args:
            credentials: ServiceNow credentials
            platform_type: Platform type (should be SERVICENOW)
        """
        super().__init__(credentials, platform_type)
        self.api_version = "v2"
        self.base_url = None
        self.session = None
        self.auth_header = None
        
    async def connect(self) -> bool:
        """
        Establish connection to ServiceNow.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            start_time = datetime.now()
            
            # Validate required credentials
            required_fields = ["username", "password", "instance_url"]
            if not PlatformUtils.validate_credentials(self.credentials.__dict__, required_fields):
                raise ValidationError("Missing required ServiceNow credentials")
            
            # Build base URL
            instance_url = self.credentials.instance_url
            if not instance_url.startswith("http"):
                instance_url = f"https://{instance_url}"
            if not instance_url.endswith(".service-now.com"):
                instance_url = f"{instance_url}.service-now.com"
            
            self.base_url = f"{instance_url}/api/now/{self.api_version}"
            
            # Create basic auth header
            credentials_str = f"{self.credentials.username}:{self.credentials.password}"
            encoded_credentials = base64.b64encode(credentials_str.encode()).decode()
            self.auth_header = f"Basic {encoded_credentials}"
            
            # Create session
            self.session = aiohttp.ClientSession()
            
            # Test connection with a simple API call
            test_url = f"{self.base_url}/table/sys_user?sysparm_limit=1"
            headers = {
                "Authorization": self.auth_header,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(test_url, headers=headers) as response:
                if response.status == 200:
                    self.connected = True
                    self.connection_time = datetime.now()
                    
                    execution_time = PlatformUtils.calculate_execution_time(start_time)
                    self._log_operation("connect", start_time, True)
                    
                    logger.info(f"Successfully connected to ServiceNow in {execution_time:.2f}s")
                    return True
                elif response.status == 401:
                    raise AuthenticationError("ServiceNow authentication failed: Invalid credentials")
                else:
                    error_text = await response.text()
                    raise PlatformConnectionError(f"ServiceNow connection failed: {error_text}")
                    
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("connect", start_time, False, str(e))
            
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            else:
                raise PlatformConnectionError(f"Failed to connect to ServiceNow: {e}")
    
    async def disconnect(self) -> bool:
        """
        Disconnect from ServiceNow.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            self.connected = False
            self.base_url = None
            self.auth_header = None
            
            logger.info("Disconnected from ServiceNow")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from ServiceNow: {e}")
            return False
    
    async def validate_credentials(self) -> bool:
        """
        Validate ServiceNow credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Basic validation - check if required fields are present
            required_fields = ["username", "password", "instance_url"]
            return PlatformUtils.validate_credentials(self.credentials.__dict__, required_fields)
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False
    
    async def get_schema(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get ServiceNow schema information.
        
        Args:
            object_type: Optional specific table to get schema for
            
        Returns:
            Dict containing schema information
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            if object_type:
                # Get specific table schema
                url = f"{self.base_url}/table/{object_type}?sysparm_display_value=true&sysparm_exclude_reference_link=true"
            else:
                # Get list of available tables
                url = f"{self.base_url}/table?sysparm_limit=1000"
            
            headers = {
                "Authorization": self.auth_header,
                "Accept": "application/json"
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    schema_data = await response.json()
                    execution_time = PlatformUtils.calculate_execution_time(start_time)
                    self._log_operation("get_schema", start_time, True)
                    return schema_data
                else:
                    error_text = await response.text()
                    raise QueryError(f"Failed to get schema: {error_text}")
                    
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("get_schema", start_time, False, str(e))
            raise QueryError(f"Schema retrieval failed: {e}")
    
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """
        Execute a query against ServiceNow.
        
        Args:
            query: Query string (table name or encoded query)
            parameters: Optional parameters for the query
            
        Returns:
            QueryResult containing query results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            # Build query URL
            if query.startswith("table/"):
                # Direct table query
                url = f"{self.base_url}/{query}"
            else:
                # Table name query
                url = f"{self.base_url}/table/{query}"
            
            # Add query parameters
            if parameters:
                query_params = []
                for key, value in parameters.items():
                    if key == "sysparm_query":
                        # URL encode the query
                        import urllib.parse
                        value = urllib.parse.quote(value)
                    query_params.append(f"{key}={value}")
                
                if query_params:
                    url += "?" + "&".join(query_params)
            
            headers = {
                "Authorization": self.auth_header,
                "Accept": "application/json"
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result_data = await response.json()
                    
                    execution_time = PlatformUtils.calculate_execution_time(start_time)
                    self._log_operation("execute_query", start_time, True)
                    
                    return QueryResult(
                        data=result_data.get("result", []),
                        total_count=len(result_data.get("result", [])),
                        success=True,
                        execution_time=execution_time,
                        query_id=PlatformUtils.generate_request_id()
                    )
                elif response.status == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitError("ServiceNow API rate limit exceeded", retry_after=retry_after)
                else:
                    error_text = await response.text()
                    raise QueryError(f"Query execution failed: {error_text}")
                    
        except RateLimitError:
            raise
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("execute_query", start_time, False, str(e))
            raise QueryError(f"Query execution failed: {e}")
    
    async def execute_action(self, action_type: ActionType, parameters: Dict[str, Any]) -> ActionResult:
        """
        Execute an action against ServiceNow.
        
        Args:
            action_type: Type of action to execute
            parameters: Parameters for the action
            
        Returns:
            ActionResult containing action results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            if action_type == ActionType.CREATE:
                return await self._create_record(parameters)
            elif action_type == ActionType.UPDATE:
                return await self._update_record(parameters)
            elif action_type == ActionType.DELETE:
                return await self._delete_record(parameters)
            elif action_type == ActionType.SEARCH:
                return await self._search_records(parameters)
            else:
                raise ActionError(f"Unsupported action type: {action_type}")
                
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("execute_action", start_time, False, str(e))
            raise ActionError(f"Action execution failed: {e}")
    
    async def search_records(self, object_type: str, criteria: Dict[str, Any]) -> QueryResult:
        """
        Search for records in ServiceNow.
        
        Args:
            object_type: Type of table to search
            criteria: Search criteria
            
        Returns:
            QueryResult containing search results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            # Build sysparm_query from criteria
            query_conditions = []
            for field, value in criteria.items():
                if isinstance(value, str):
                    query_conditions.append(f"{field}={value}")
                elif isinstance(value, (int, float)):
                    query_conditions.append(f"{field}={value}")
                else:
                    query_conditions.append(f"{field}={str(value)}")
            
            sysparm_query = "^".join(query_conditions) if query_conditions else ""
            
            # Execute the query
            parameters = {"sysparm_query": sysparm_query} if sysparm_query else {}
            result = await self.execute_query(object_type, parameters)
            
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("search_records", start_time, True)
            
            return result
            
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("search_records", start_time, False, str(e))
            raise QueryError(f"Record search failed: {e}")
    
    async def create_record(self, object_type: str, data: Dict[str, Any]) -> ActionResult:
        """
        Create a new record in ServiceNow.
        
        Args:
            object_type: Type of table to create record in
            data: Data for the new record
            
        Returns:
            ActionResult containing creation results
        """
        return await self._create_record({"object_type": object_type, "data": data})
    
    async def update_record(self, object_type: str, record_id: str, data: Dict[str, Any]) -> ActionResult:
        """
        Update an existing record in ServiceNow.
        
        Args:
            object_type: Type of table to update
            record_id: Sys ID of the record to update
            data: Updated data for the record
            
        Returns:
            ActionResult containing update results
        """
        return await self._update_record({
            "object_type": object_type,
            "record_id": record_id,
            "data": data
        })
    
    async def delete_record(self, object_type: str, record_id: str) -> ActionResult:
        """
        Delete a record from ServiceNow.
        
        Args:
            object_type: Type of table to delete from
            record_id: Sys ID of the record to delete
            
        Returns:
            ActionResult containing deletion results
        """
        return await self._delete_record({
            "object_type": object_type,
            "record_id": record_id
        })
    
    async def _create_record(self, parameters: Dict[str, Any]) -> ActionResult:
        """Internal method to create a record."""
        object_type = parameters["object_type"]
        data = parameters["data"]
        
        url = f"{self.base_url}/table/{object_type}"
        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        async with self.session.post(url, headers=headers, json=data) as response:
            if response.status in [200, 201]:
                result_data = await response.json()
                return ActionResult(
                    success=True,
                    record_id=result_data.get("result", {}).get("sys_id"),
                    data=result_data.get("result", {}),
                    execution_time=0.0,
                    action_id=PlatformUtils.generate_request_id()
                )
            else:
                error_text = await response.text()
                return ActionResult(
                    success=False,
                    error_message=f"Record creation failed: {error_text}",
                    execution_time=0.0
                )
    
    async def _update_record(self, parameters: Dict[str, Any]) -> ActionResult:
        """Internal method to update a record."""
        object_type = parameters["object_type"]
        record_id = parameters["record_id"]
        data = parameters["data"]
        
        url = f"{self.base_url}/table/{object_type}/{record_id}"
        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        async with self.session.put(url, headers=headers, json=data) as response:
            if response.status == 200:
                result_data = await response.json()
                return ActionResult(
                    success=True,
                    record_id=record_id,
                    data=result_data.get("result", {}),
                    execution_time=0.0,
                    action_id=PlatformUtils.generate_request_id()
                )
            else:
                error_text = await response.text()
                return ActionResult(
                    success=False,
                    error_message=f"Record update failed: {error_text}",
                    execution_time=0.0
                )
    
    async def _delete_record(self, parameters: Dict[str, Any]) -> ActionResult:
        """Internal method to delete a record."""
        object_type = parameters["object_type"]
        record_id = parameters["record_id"]
        
        url = f"{self.base_url}/table/{object_type}/{record_id}"
        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json"
        }
        
        async with self.session.delete(url, headers=headers) as response:
            if response.status == 204:
                return ActionResult(
                    success=True,
                    record_id=record_id,
                    execution_time=0.0,
                    action_id=PlatformUtils.generate_request_id()
                )
            else:
                error_text = await response.text()
                return ActionResult(
                    success=False,
                    error_message=f"Record deletion failed: {error_text}",
                    execution_time=0.0
                )
    
    async def _search_records(self, parameters: Dict[str, Any]) -> ActionResult:
        """Internal method to search records."""
        object_type = parameters.get("object_type", "incident")
        criteria = parameters.get("criteria", {})
        
        query_result = await self.search_records(object_type, criteria)
        
        return ActionResult(
            success=query_result.success,
            data=query_result.data,
            error_message=query_result.error_message,
            execution_time=query_result.execution_time,
            action_id=PlatformUtils.generate_request_id()
        )
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """
        Perform ServiceNow-specific health check.
        
        Returns:
            Dict containing health check results
        """
        try:
            # Simple query to test connectivity
            url = f"{self.base_url}/table/sys_user?sysparm_limit=1"
            headers = {
                "Authorization": self.auth_header,
                "Accept": "application/json"
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return {
                        "healthy": True,
                        "api_version": self.api_version,
                        "instance_url": self.base_url
                    }
                else:
                    return {
                        "healthy": False,
                        "error": f"Health check failed with status {response.status}"
                    }
                    
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
