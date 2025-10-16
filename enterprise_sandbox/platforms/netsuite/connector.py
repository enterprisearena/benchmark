"""
NetSuite Platform Connector

This module implements the NetSuite platform connector for EnterpriseArena.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp
import json
import hashlib
import hmac
import base64
import urllib.parse
from urllib.parse import urlencode

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


class NetSuiteConnector(BasePlatform):
    """
    NetSuite platform connector implementation.
    
    This class provides the concrete implementation for connecting to and
    interacting with NetSuite using the REST API and SuiteScript.
    """
    
    def __init__(self, credentials: PlatformCredentials, platform_type: PlatformType):
        """
        Initialize NetSuite connector.
        
        Args:
            credentials: NetSuite credentials
            platform_type: Platform type (should be NETSUITE)
        """
        super().__init__(credentials, platform_type)
        self.api_version = "2023.2"
        self.base_url = None
        self.session = None
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
    async def connect(self) -> bool:
        """
        Establish connection to NetSuite.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            start_time = datetime.now()
            
            # Validate required credentials
            required_fields = ["username", "password", "account_id", "role_id", 
                             "application_id", "consumer_key", "consumer_secret", 
                             "token_id", "token_secret"]
            if not PlatformUtils.validate_credentials(self.credentials.__dict__, required_fields):
                raise ValidationError("Missing required NetSuite credentials")
            
            # Build base URL
            account_id = self.credentials.account_id
            if self.credentials.environment == "sandbox":
                self.base_url = f"https://{account_id}.app.netsuite.com"
            else:
                self.base_url = f"https://{account_id}.app.netsuite.com"
            
            # Create session
            self.session = aiohttp.ClientSession()
            
            # Authenticate using OAuth 1.0a
            await self._authenticate_oauth()
            
            self.connected = True
            self.connection_time = datetime.now()
            
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("connect", start_time, True)
            
            logger.info(f"Successfully connected to NetSuite in {execution_time:.2f}s")
            return True
            
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("connect", start_time, False, str(e))
            
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            else:
                raise PlatformConnectionError(f"Failed to connect to NetSuite: {e}")
    
    async def _authenticate_oauth(self):
        """Authenticate using OAuth 1.0a."""
        try:
            # OAuth 1.0a parameters
            oauth_params = {
                "oauth_consumer_key": self.credentials.consumer_key,
                "oauth_token": self.credentials.token_id,
                "oauth_signature_method": "HMAC-SHA256",
                "oauth_timestamp": str(int(datetime.now().timestamp())),
                "oauth_nonce": self._generate_nonce(),
                "oauth_version": "1.0"
            }
            
            # Create signature
            signature = self._create_oauth_signature(oauth_params)
            oauth_params["oauth_signature"] = signature
            
            # Create OAuth header
            oauth_header = "OAuth " + ", ".join([
                f'{k}="{v}"' for k, v in oauth_params.items()
            ])
            
            # Test connection with a simple API call
            test_url = f"{self.base_url}/services/rest/record/v1/metadata-catalog"
            headers = {
                "Authorization": oauth_header,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(test_url, headers=headers) as response:
                if response.status == 200:
                    logger.info("NetSuite OAuth authentication successful")
                elif response.status == 401:
                    raise AuthenticationError("NetSuite OAuth authentication failed")
                else:
                    error_text = await response.text()
                    raise AuthenticationError(f"NetSuite authentication failed: {error_text}")
                    
        except Exception as e:
            raise AuthenticationError(f"OAuth authentication failed: {e}")
    
    def _generate_nonce(self) -> str:
        """Generate OAuth nonce."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _create_oauth_signature(self, params: Dict[str, str]) -> str:
        """Create OAuth 1.0a signature."""
        # Create signature base string
        base_string = "GET&" + urllib.parse.quote(self.base_url + "/services/rest/record/v1/metadata-catalog", safe="")
        base_string += "&" + urllib.parse.quote(urlencode(sorted(params.items())), safe="")
        
        # Create signing key
        signing_key = urllib.parse.quote(self.credentials.consumer_secret, safe="") + "&" + urllib.parse.quote(self.credentials.token_secret, safe="")
        
        # Create signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    async def disconnect(self) -> bool:
        """
        Disconnect from NetSuite.
        
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
            
            logger.info("Disconnected from NetSuite")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from NetSuite: {e}")
            return False
    
    async def validate_credentials(self) -> bool:
        """
        Validate NetSuite credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Basic validation - check if required fields are present
            required_fields = ["username", "password", "account_id", "role_id", 
                             "application_id", "consumer_key", "consumer_secret", 
                             "token_id", "token_secret"]
            return PlatformUtils.validate_credentials(self.credentials.__dict__, required_fields)
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False
    
    async def get_schema(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get NetSuite schema information.
        
        Args:
            object_type: Optional specific record type to get schema for
            
        Returns:
            Dict containing schema information
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            if object_type:
                # Get specific record type schema
                url = f"{self.base_url}/services/rest/record/v1/metadata-catalog/{object_type}"
            else:
                # Get metadata catalog
                url = f"{self.base_url}/services/rest/record/v1/metadata-catalog"
            
            headers = self._get_auth_headers()
            
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
        Execute a query against NetSuite.
        
        Args:
            query: Query string (record type or SuiteQL query)
            parameters: Optional parameters for the query
            
        Returns:
            QueryResult containing query results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            # Build query URL
            if query.startswith("SELECT") or query.startswith("select"):
                # SuiteQL query
                url = f"{self.base_url}/services/rest/query/v1/suiteql"
                headers = self._get_auth_headers()
                
                # Execute SuiteQL query
                query_data = {"q": query}
                async with self.session.post(url, headers=headers, json=query_data) as response:
                    if response.status == 200:
                        result_data = await response.json()
                    else:
                        error_text = await response.text()
                        raise QueryError(f"SuiteQL query failed: {error_text}")
            else:
                # Record type query
                url = f"{self.base_url}/services/rest/record/v1/{query}"
                
                # Add query parameters
                if parameters:
                    query_params = []
                    for key, value in parameters.items():
                        query_params.append(f"{key}={value}")
                    
                    if query_params:
                        url += "?" + "&".join(query_params)
                
                headers = self._get_auth_headers()
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result_data = await response.json()
                    else:
                        error_text = await response.text()
                        raise QueryError(f"Record query failed: {error_text}")
            
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("execute_query", start_time, True)
            
            return QueryResult(
                data=result_data.get("items", result_data.get("result", [])),
                total_count=len(result_data.get("items", result_data.get("result", []))),
                success=True,
                execution_time=execution_time,
                query_id=PlatformUtils.generate_request_id()
            )
                    
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("execute_query", start_time, False, str(e))
            raise QueryError(f"Query execution failed: {e}")
    
    async def execute_action(self, action_type: ActionType, parameters: Dict[str, Any]) -> ActionResult:
        """
        Execute an action against NetSuite.
        
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
        Search for records in NetSuite.
        
        Args:
            object_type: Type of record to search
            criteria: Search criteria
            
        Returns:
            QueryResult containing search results
        """
        self._validate_connection()
        
        try:
            start_time = datetime.now()
            
            # Build SuiteQL query from criteria
            where_conditions = []
            for field, value in criteria.items():
                if isinstance(value, str):
                    where_conditions.append(f"{field} = '{value}'")
                elif isinstance(value, (int, float)):
                    where_conditions.append(f"{field} = {value}")
                else:
                    where_conditions.append(f"{field} = '{str(value)}'")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            suiteql_query = f"SELECT * FROM {object_type} WHERE {where_clause}"
            
            # Execute the query
            result = await self.execute_query(suiteql_query)
            
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("search_records", start_time, True)
            
            return result
            
        except Exception as e:
            execution_time = PlatformUtils.calculate_execution_time(start_time)
            self._log_operation("search_records", start_time, False, str(e))
            raise QueryError(f"Record search failed: {e}")
    
    async def create_record(self, object_type: str, data: Dict[str, Any]) -> ActionResult:
        """
        Create a new record in NetSuite.
        
        Args:
            object_type: Type of record to create
            data: Data for the new record
            
        Returns:
            ActionResult containing creation results
        """
        return await self._create_record({"object_type": object_type, "data": data})
    
    async def update_record(self, object_type: str, record_id: str, data: Dict[str, Any]) -> ActionResult:
        """
        Update an existing record in NetSuite.
        
        Args:
            object_type: Type of record to update
            record_id: Internal ID of the record to update
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
        Delete a record from NetSuite.
        
        Args:
            object_type: Type of record to delete
            record_id: Internal ID of the record to delete
            
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
        
        url = f"{self.base_url}/services/rest/record/v1/{object_type}"
        headers = self._get_auth_headers()
        
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
        
        url = f"{self.base_url}/services/rest/record/v1/{object_type}/{record_id}"
        headers = self._get_auth_headers()
        
        async with self.session.put(url, headers=headers, json=data) as response:
            if response.status == 200:
                result_data = await response.json()
                return ActionResult(
                    success=True,
                    record_id=record_id,
                    data=result_data,
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
        
        url = f"{self.base_url}/services/rest/record/v1/{object_type}/{record_id}"
        headers = self._get_auth_headers()
        
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
        object_type = parameters.get("object_type", "customer")
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
        # OAuth 1.0a parameters
        oauth_params = {
            "oauth_consumer_key": self.credentials.consumer_key,
            "oauth_token": self.credentials.token_id,
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": str(int(datetime.now().timestamp())),
            "oauth_nonce": self._generate_nonce(),
            "oauth_version": "1.0"
        }
        
        # Create signature
        signature = self._create_oauth_signature(oauth_params)
        oauth_params["oauth_signature"] = signature
        
        # Create OAuth header
        oauth_header = "OAuth " + ", ".join([
            f'{k}="{v}"' for k, v in oauth_params.items()
        ])
        
        return {
            "Authorization": oauth_header,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """
        Perform NetSuite-specific health check.
        
        Returns:
            Dict containing health check results
        """
        try:
            # Simple query to test connectivity
            url = f"{self.base_url}/services/rest/record/v1/metadata-catalog"
            headers = self._get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return {
                        "healthy": True,
                        "api_version": self.api_version,
                        "base_url": self.base_url
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
