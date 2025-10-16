"""
Salesforce Platform Connector

This module implements the Salesforce platform connector for EnterpriseArena.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp
import json

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


class SalesforceConnector(BasePlatform):
    """
    Salesforce platform connector implementation.
    
    This class provides the concrete implementation for connecting to and
    interacting with Salesforce using the REST API.
    """
    
    def __init__(self, credentials: PlatformCredentials, platform_type: PlatformType):
        """
        Initialize Salesforce connector.
        
        Args:
            credentials: Salesforce credentials
            platform_type: Platform type (should be SALESFORCE)
        """
        super().__init__(credentials, platform_type)
        self.api_version = "v58.0"
        self.base_url = None
        self.access_token = None
        self.session = None
        
    async def connect(self) -> bool:
        """
        Establish connection to Salesforce.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            start_time = datetime.now()
            
            # Validate required credentials
            required_fields = ["username", "password", "security_token"]
            if not PlatformUtils.validate_credentials(self.credentials.__dict__, required_fields):
                raise ValidationError("Missing required Salesforce credentials")
            
            # Build login URL
            if self.credentials.instance_url:
                login_url = f"{self.credentials.instance_url}/services/oauth2/token"
            else:
                # Use production or sandbox based on environment
                domain = "login" if self.credentials.environment == "production" else "test"
                login_url = f"https://{domain}.salesforce.com/services/oauth2/token"
            
            # Prepare login data
            login_data = {
                "grant_type": "password",
                "client_id": self.credentials.client_id or "3MVG9fMtCkV6eLheIEZplMqWfnGlf3Y.BcWdOf1qytXo9zxgbsrUbS.ExHTgUPJeb3jZeT8NYhcHQMyT7B6aB",
                "client_secret": self.credentials.client_secret or "6189767886681647722",
                "username": self.credentials.username,
                "password": f"{self.credentials.password}{self.credentials.security_token}"
            }
            
            # Create session and authenticate
            self.session = aiohttp.ClientSession()
            
            async with self.session.post(login_url, data=login_data) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    self.access_token = auth_data["access_token"]
                    self.base_url = auth_data["instance_url"]
                    
                    self.connected = True
                    self.connection_time = datetime.now()
                    
                    execution_time = PlatformUtils.calculate_execution_time(start_time)
                    self._log_operation("connect", start_time, True)
                    
                    logger.info(f"Successfully connected to Salesforce in {execution_time:.2f}s")
                    return True
                else:
                    error_text = await response.text()
                    raise AuthenticationError(f"Salesforce authentication failed: {error_text}")
                    
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("connect", start_time, False, str(e))
            
            if isinstance(e, AuthenticationError):
                raise
            else:
                raise PlatformConnectionError(f"Failed to connect to Salesforce: {e}")
    
    async def disconnect(self) -> bool:
        """
        Disconnect from Salesforce.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            self.connected = False
            self.access_token = None
            self.base_url = None
            
            logger.info("Disconnected from Salesforce")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Salesforce: {e}")
            return False
    
    async def validate_credentials(self) -> bool:
        """
        Validate Salesforce credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Basic validation - check if required fields are present
            required_fields = ["username", "password", "security_token"]
            return PlatformUtils.validate_credentials(self.credentials.__dict__, required_fields)
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False
    
    async def get_schema(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Salesforce schema information.
        
        Args:
            object_type: Optional specific object type to get schema for
            
        Returns:
            Dict containing schema information
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            if object_type:
                # Get specific object schema
                url = f"{self.base_url}/services/data/{self.api_version}/sobjects/{object_type}/describe"
            else:
                # Get global schema
                url = f"{self.base_url}/services/data/{self.api_version}/sobjects"
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
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
        Execute a SOQL query against Salesforce.
        
        Args:
            query: SOQL query string
            parameters: Optional parameters for the query
            
        Returns:
            QueryResult containing query results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            # Sanitize query
            sanitized_query = PlatformUtils.sanitize_query(query)
            
            # URL encode the query
            import urllib.parse
            encoded_query = urllib.parse.quote(sanitized_query)
            url = f"{self.base_url}/services/data/{self.api_version}/query/?q={encoded_query}"
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result_data = await response.json()
                    
                    execution_time = PlatformUtils.calculate_execution_time(start_time)
                    self._log_operation("execute_query", start_time, True)
                    
                    return QueryResult(
                        data=result_data.get("records", []),
                        total_count=result_data.get("totalSize", 0),
                        success=True,
                        execution_time=execution_time,
                        query_id=PlatformUtils.generate_request_id()
                    )
                elif response.status == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitError("Salesforce API rate limit exceeded", retry_after=retry_after)
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
        Execute an action against Salesforce.
        
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
        Search for records in Salesforce.
        
        Args:
            object_type: Type of object to search for
            criteria: Search criteria
            
        Returns:
            QueryResult containing search results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            # Build SOQL query from criteria
            where_clause = PlatformUtils.build_where_clause(criteria)
            query = f"SELECT Id, Name FROM {object_type}"
            if where_clause:
                query += f" WHERE {where_clause}"
            query += " LIMIT 200"
            
            # Execute the query
            result = await self.execute_query(query)
            
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("search_records", start_time, True)
            
            return result
            
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("search_records", start_time, False, str(e))
            raise QueryError(f"Record search failed: {e}")
    
    async def create_record(self, object_type: str, data: Dict[str, Any]) -> ActionResult:
        """
        Create a new record in Salesforce.
        
        Args:
            object_type: Type of object to create
            data: Data for the new record
            
        Returns:
            ActionResult containing creation results
        """
        return await self._create_record({"object_type": object_type, "data": data})
    
    async def update_record(self, object_type: str, record_id: str, data: Dict[str, Any]) -> ActionResult:
        """
        Update an existing record in Salesforce.
        
        Args:
            object_type: Type of object to update
            record_id: ID of the record to update
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
        Delete a record from Salesforce.
        
        Args:
            object_type: Type of object to delete
            record_id: ID of the record to delete
            
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
        
        url = f"{self.base_url}/services/data/{self.api_version}/sobjects/{object_type}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with self.session.post(url, headers=headers, json=data) as response:
            if response.status in [200, 201]:
                result_data = await response.json()
                return ActionResult(
                    success=True,
                    record_id=result_data.get("id"),
                    data=result_data,
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
        
        url = f"{self.base_url}/services/data/{self.api_version}/sobjects/{object_type}/{record_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with self.session.patch(url, headers=headers, json=data) as response:
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
                    error_message=f"Record update failed: {error_text}",
                    execution_time=0.0
                )
    
    async def _delete_record(self, parameters: Dict[str, Any]) -> ActionResult:
        """Internal method to delete a record."""
        object_type = parameters["object_type"]
        record_id = parameters["record_id"]
        
        url = f"{self.base_url}/services/data/{self.api_version}/sobjects/{object_type}/{record_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
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
        # This would be implemented for search-specific functionality
        # For now, delegate to search_records method
        object_type = parameters.get("object_type", "Account")
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
        Perform Salesforce-specific health check.
        
        Returns:
            Dict containing health check results
        """
        try:
            # Simple query to test connectivity
            url = f"{self.base_url}/services/data/{self.api_version}/sobjects"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
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
