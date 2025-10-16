"""
QuickBooks Platform Connector

This module implements the QuickBooks platform connector for EnterpriseArena.
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


class QuickBooksConnector(BasePlatform):
    """
    QuickBooks platform connector implementation.
    
    This class provides the concrete implementation for connecting to and
    interacting with QuickBooks using the REST API.
    """
    
    def __init__(self, credentials: PlatformCredentials, platform_type: PlatformType):
        """
        Initialize QuickBooks connector.
        
        Args:
            credentials: QuickBooks credentials
            platform_type: Platform type (should be QUICKBOOKS)
        """
        super().__init__(credentials, platform_type)
        self.api_version = "v3"
        self.base_url = None
        self.session = None
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.company_id = None
        
    async def connect(self) -> bool:
        """
        Establish connection to QuickBooks.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            start_time = datetime.now()
            
            # Validate required credentials
            required_fields = ["client_id", "client_secret", "company_id", "access_token"]
            if not PlatformUtils.validate_credentials(self.credentials.__dict__, required_fields):
                raise ValidationError("Missing required QuickBooks credentials")
            
            # Set company ID
            self.company_id = self.credentials.company_id
            
            # Build base URL
            if self.credentials.environment == "sandbox":
                self.base_url = "https://sandbox-quickbooks.api.intuit.com"
            else:
                self.base_url = "https://quickbooks.api.intuit.com"
            
            # Create session
            self.session = aiohttp.ClientSession()
            
            # Set access token
            self.access_token = self.credentials.access_token
            
            # Test connection with a simple API call
            test_url = f"{self.base_url}/v3/company/{self.company_id}/companyinfo/{self.company_id}"
            headers = self._get_auth_headers()
            
            async with self.session.get(test_url, headers=headers) as response:
                if response.status == 200:
                    self.connected = True
                    self.connection_time = datetime.now()
                    
                    execution_time = PlatformUtils.calculate_execution_time(start_time)
                    self._log_operation("connect", start_time, True)
                    
                    logger.info(f"Successfully connected to QuickBooks in {execution_time:.2f}s")
                    return True
                elif response.status == 401:
                    # Try to refresh token if available
                    if self.credentials.refresh_token:
                        await self._refresh_access_token()
                        return await self.connect()  # Retry connection
                    else:
                        raise AuthenticationError("QuickBooks authentication failed: Invalid access token")
                else:
                    error_text = await response.text()
                    raise PlatformConnectionError(f"QuickBooks connection failed: {error_text}")
                    
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("connect", start_time, False, str(e))
            
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            else:
                raise PlatformConnectionError(f"Failed to connect to QuickBooks: {e}")
    
    async def _refresh_access_token(self):
        """Refresh the access token using refresh token."""
        try:
            if not self.credentials.refresh_token:
                raise AuthenticationError("No refresh token available")
            
            # Prepare refresh token request
            refresh_data = {
                "grant_type": "refresh_token",
                "refresh_token": self.credentials.refresh_token
            }
            
            # Create basic auth header
            credentials_str = f"{self.credentials.client_id}:{self.credentials.client_secret}"
            encoded_credentials = base64.b64encode(credentials_str.encode()).decode()
            auth_header = f"Basic {encoded_credentials}"
            
            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Make refresh request
            refresh_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
            async with self.session.post(refresh_url, headers=headers, data=refresh_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data["access_token"]
                    self.refresh_token = token_data.get("refresh_token", self.credentials.refresh_token)
                    
                    # Calculate expiration time
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = datetime.now().timestamp() + expires_in
                    
                    logger.info("QuickBooks access token refreshed successfully")
                else:
                    error_text = await response.text()
                    raise AuthenticationError(f"Token refresh failed: {error_text}")
                    
        except Exception as e:
            raise AuthenticationError(f"Failed to refresh access token: {e}")
    
    async def disconnect(self) -> bool:
        """
        Disconnect from QuickBooks.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            self.connected = False
            self.base_url = None
            self.access_token = None
            self.refresh_token = None
            self.token_expires_at = None
            self.company_id = None
            
            logger.info("Disconnected from QuickBooks")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from QuickBooks: {e}")
            return False
    
    async def validate_credentials(self) -> bool:
        """
        Validate QuickBooks credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Basic validation - check if required fields are present
            required_fields = ["client_id", "client_secret", "company_id", "access_token"]
            return PlatformUtils.validate_credentials(self.credentials.__dict__, required_fields)
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False
    
    async def get_schema(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get QuickBooks schema information.
        
        Args:
            object_type: Optional specific entity to get schema for
            
        Returns:
            Dict containing schema information
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            if object_type:
                # Get specific entity schema
                url = f"{self.base_url}/v3/company/{self.company_id}/query"
                query = f"SELECT * FROM {object_type} MAXRESULTS 1"
                params = {"query": query}
            else:
                # Get company info as schema reference
                url = f"{self.base_url}/v3/company/{self.company_id}/companyinfo/{self.company_id}"
                params = {}
            
            headers = self._get_auth_headers()
            
            async with self.session.get(url, headers=headers, params=params) as response:
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
        Execute a query against QuickBooks.
        
        Args:
            query: Query string (entity name or SQL-like query)
            parameters: Optional parameters for the query
            
        Returns:
            QueryResult containing query results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            # Build query URL
            if query.startswith("SELECT") or query.startswith("select"):
                # SQL-like query
                url = f"{self.base_url}/v3/company/{self.company_id}/query"
                params = {"query": query}
            else:
                # Entity name query
                url = f"{self.base_url}/v3/company/{self.company_id}/query"
                params = {"query": f"SELECT * FROM {query}"}
            
            # Add additional parameters
            if parameters:
                for key, value in parameters.items():
                    params[key] = value
            
            headers = self._get_auth_headers()
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result_data = await response.json()
                    
                    execution_time = PlatformUtils.calculate_execution_time(start_time)
                    self._log_operation("execute_query", start_time, True)
                    
                    # Extract entities from QuickBooks response
                    entities = []
                    if "QueryResponse" in result_data:
                        entities = result_data["QueryResponse"].get(query.split()[2] if "SELECT" in query else query, [])
                        if not isinstance(entities, list):
                            entities = [entities] if entities else []
                    
                    return QueryResult(
                        data=entities,
                        total_count=len(entities),
                        success=True,
                        execution_time=execution_time,
                        query_id=PlatformUtils.generate_request_id()
                    )
                elif response.status == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitError("QuickBooks API rate limit exceeded", retry_after=retry_after)
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
        Execute an action against QuickBooks.
        
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
        Search for records in QuickBooks.
        
        Args:
            object_type: Type of entity to search
            criteria: Search criteria
            
        Returns:
            QueryResult containing search results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            # Build WHERE clause from criteria
            where_conditions = []
            for field, value in criteria.items():
                if isinstance(value, str):
                    where_conditions.append(f"{field} = '{value}'")
                elif isinstance(value, (int, float)):
                    where_conditions.append(f"{field} = {value}")
                else:
                    where_conditions.append(f"{field} = '{str(value)}'")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            query = f"SELECT * FROM {object_type} WHERE {where_clause}"
            
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
        Create a new record in QuickBooks.
        
        Args:
            object_type: Type of entity to create
            data: Data for the new record
            
        Returns:
            ActionResult containing creation results
        """
        return await self._create_record({"object_type": object_type, "data": data})
    
    async def update_record(self, object_type: str, record_id: str, data: Dict[str, Any]) -> ActionResult:
        """
        Update an existing record in QuickBooks.
        
        Args:
            object_type: Type of entity to update
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
        Delete a record from QuickBooks.
        
        Args:
            object_type: Type of entity to delete
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
        
        url = f"{self.base_url}/v3/company/{self.company_id}/{object_type.lower()}"
        headers = self._get_auth_headers()
        
        # Wrap data in QuickBooks format
        payload = {object_type: data}
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status in [200, 201]:
                result_data = await response.json()
                entity = result_data.get(object_type, [{}])[0] if isinstance(result_data.get(object_type), list) else result_data.get(object_type, {})
                return ActionResult(
                    success=True,
                    record_id=entity.get("Id"),
                    data=entity,
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
        
        url = f"{self.base_url}/v3/company/{self.company_id}/{object_type.lower()}"
        headers = self._get_auth_headers()
        
        # Add ID to data for update
        data["Id"] = record_id
        data["SyncToken"] = "1"  # Required for updates
        
        # Wrap data in QuickBooks format
        payload = {object_type: data}
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                result_data = await response.json()
                entity = result_data.get(object_type, [{}])[0] if isinstance(result_data.get(object_type), list) else result_data.get(object_type, {})
                return ActionResult(
                    success=True,
                    record_id=record_id,
                    data=entity,
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
        
        url = f"{self.base_url}/v3/company/{self.company_id}/{object_type.lower()}"
        headers = self._get_auth_headers()
        
        # Create delete payload
        delete_data = {
            "Id": record_id,
            "SyncToken": "1"
        }
        payload = {object_type: delete_data}
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
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
        object_type = parameters.get("object_type", "Customer")
        criteria = parameters.get("criteria", {})
        
        query_result = await self.search_records(object_type, criteria)
        
        return ActionResult(
            success=query_result.success,
            data=query_result.data,
            error_message=query_result.error_message,
            execution_time=query_result.execution_time,
            action_id=PlatformUtils.generate_request_id()
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """
        Perform QuickBooks-specific health check.
        
        Returns:
            Dict containing health check results
        """
        try:
            # Simple query to test connectivity
            url = f"{self.base_url}/v3/company/{self.company_id}/companyinfo/{self.company_id}"
            headers = self._get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return {
                        "healthy": True,
                        "api_version": self.api_version,
                        "base_url": self.base_url,
                        "company_id": self.company_id
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
