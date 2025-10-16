# EnterpriseArena Platform Abstraction Layer

## Overview
The platform abstraction layer provides a unified interface for interacting with different enterprise software platforms, enabling seamless integration and consistent agent behavior across multiple systems.

## Base Platform Interface

### Core Platform Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

class PlatformType(Enum):
    CRM = "crm"
    ERP = "erp"
    ACCOUNTING = "accounting"
    ITSM = "itsm"
    HR = "hr"
    MARKETING = "marketing"

class ActionType(Enum):
    QUERY = "query"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    EXECUTE = "execute"

@dataclass
class PlatformCredentials:
    """Standardized credential structure for all platforms"""
    username: str
    password: str
    api_key: Optional[str] = None
    security_token: Optional[str] = None
    instance_url: Optional[str] = None
    environment: str = "production"  # production, sandbox, development

@dataclass
class QueryResult:
    """Standardized query result structure"""
    data: List[Dict[str, Any]]
    total_count: int
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0

@dataclass
class ActionResult:
    """Standardized action result structure"""
    success: bool
    record_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0

class BasePlatform(ABC):
    """Abstract base class for all platform implementations"""
    
    def __init__(self, credentials: PlatformCredentials, platform_type: PlatformType):
        self.credentials = credentials
        self.platform_type = platform_type
        self.connection = None
        self.schema_cache = {}
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the platform"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to the platform"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate platform credentials"""
        pass
    
    @abstractmethod
    async def get_schema(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """Get platform schema information"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a query on the platform"""
        pass
    
    @abstractmethod
    async def execute_action(self, action_type: ActionType, parameters: Dict[str, Any]) -> ActionResult:
        """Execute an action on the platform"""
        pass
    
    @abstractmethod
    async def search_records(self, object_type: str, criteria: Dict[str, Any]) -> QueryResult:
        """Search for records using platform-specific criteria"""
        pass
    
    @abstractmethod
    async def create_record(self, object_type: str, data: Dict[str, Any]) -> ActionResult:
        """Create a new record"""
        pass
    
    @abstractmethod
    async def update_record(self, object_type: str, record_id: str, data: Dict[str, Any]) -> ActionResult:
        """Update an existing record"""
        pass
    
    @abstractmethod
    async def delete_record(self, object_type: str, record_id: str) -> ActionResult:
        """Delete a record"""
        pass
    
    # Common utility methods
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information"""
        return {
            "platform_type": self.platform_type.value,
            "is_connected": self.is_connected,
            "credentials_valid": self.credentials is not None
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform platform health check"""
        try:
            schema = await self.get_schema()
            return {
                "status": "healthy",
                "connection": self.is_connected,
                "schema_accessible": schema is not None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

## Platform-Specific Implementations

### Salesforce Platform Implementation
```python
import simple_salesforce
from simple_salesforce import Salesforce

class SalesforcePlatform(BasePlatform):
    """Salesforce platform implementation"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials, PlatformType.CRM)
        self.sf = None
    
    async def connect(self) -> bool:
        """Connect to Salesforce using simple-salesforce"""
        try:
            self.sf = Salesforce(
                username=self.credentials.username,
                password=self.credentials.password,
                security_token=self.credentials.security_token,
                domain='test' if self.credentials.environment == 'sandbox' else 'login'
            )
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Salesforce connection failed: {e}")
            return False
    
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute SOQL/SOSL query"""
        start_time = time.time()
        try:
            if query.strip().upper().startswith('SELECT'):
                # SOQL query
                result = self.sf.query(query)
                data = result['records']
                total_count = result['totalSize']
            else:
                # SOSL query
                result = self.sf.search(query)
                data = result
                total_count = len(data)
            
            execution_time = time.time() - start_time
            return QueryResult(
                data=data,
                total_count=total_count,
                success=True,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                data=[],
                total_count=0,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def get_schema(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """Get Salesforce schema"""
        try:
            if object_type:
                if object_type in self.schema_cache:
                    return self.schema_cache[object_type]
                
                describe = self.sf.__getattr__(object_type).describe()
                schema = {
                    "object": object_type,
                    "fields": {field['name']: field['type'] for field in describe['fields']},
                    "relationships": [rel['name'] for rel in describe.get('childRelationships', [])]
                }
                self.schema_cache[object_type] = schema
                return schema
            else:
                # Get all objects
                objects = self.sf.describe()['sobjects']
                return {
                    "objects": [obj['name'] for obj in objects if obj['queryable']],
                    "total_objects": len(objects)
                }
        except Exception as e:
            raise Exception(f"Failed to get schema: {e}")
    
    async def create_record(self, object_type: str, data: Dict[str, Any]) -> ActionResult:
        """Create record in Salesforce"""
        start_time = time.time()
        try:
            result = self.sf.__getattr__(object_type).create(data)
            execution_time = time.time() - start_time
            
            return ActionResult(
                success=True,
                record_id=result['id'],
                data=result,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ActionResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
```

### ServiceNow Platform Implementation
```python
import requests
import json

class ServiceNowPlatform(BasePlatform):
    """ServiceNow platform implementation"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials, PlatformType.ITSM)
        self.base_url = f"https://{credentials.instance_url}.service-now.com"
        self.session = None
    
    async def connect(self) -> bool:
        """Connect to ServiceNow using REST API"""
        try:
            self.session = requests.Session()
            self.session.auth = (self.credentials.username, self.credentials.password)
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            # Test connection
            response = self.session.get(f"{self.base_url}/api/now/table/sys_user?sysparm_limit=1")
            if response.status_code == 200:
                self.is_connected = True
                return True
            else:
                return False
        except Exception as e:
            print(f"ServiceNow connection failed: {e}")
            return False
    
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute ServiceNow query"""
        start_time = time.time()
        try:
            # Parse table name from query (simplified)
            table_name = self._extract_table_name(query)
            
            # Build query parameters
            params = {
                'sysparm_query': query,
                'sysparm_limit': parameters.get('limit', 100) if parameters else 100
            }
            
            response = self.session.get(f"{self.base_url}/api/now/table/{table_name}", params=params)
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('result', [])
                total_count = len(data)
                
                execution_time = time.time() - start_time
                return QueryResult(
                    data=data,
                    total_count=total_count,
                    success=True,
                    execution_time=execution_time
                )
            else:
                execution_time = time.time() - start_time
                return QueryResult(
                    data=[],
                    total_count=0,
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}",
                    execution_time=execution_time
                )
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                data=[],
                total_count=0,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from ServiceNow query"""
        # Simplified extraction - in practice, would need proper parsing
        if 'FROM' in query.upper():
            parts = query.upper().split('FROM')
            if len(parts) > 1:
                return parts[1].strip().split()[0].lower()
        return 'incident'  # Default table
```

### NetSuite Platform Implementation
```python
import netsuite
from netsuite import NetSuite

class NetSuitePlatform(BasePlatform):
    """NetSuite platform implementation"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials, PlatformType.ERP)
        self.ns = None
    
    async def connect(self) -> bool:
        """Connect to NetSuite using SuiteTalk"""
        try:
            self.ns = NetSuite(
                account_id=self.credentials.instance_url,
                consumer_key=self.credentials.api_key,
                consumer_secret=self.credentials.password,
                token_id=self.credentials.username,
                token_secret=self.credentials.security_token
            )
            self.is_connected = True
            return True
        except Exception as e:
            print(f"NetSuite connection failed: {e}")
            return False
    
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute NetSuite SuiteQL query"""
        start_time = time.time()
        try:
            result = self.ns.query(query)
            data = result.get('items', [])
            total_count = result.get('totalResults', len(data))
            
            execution_time = time.time() - start_time
            return QueryResult(
                data=data,
                total_count=total_count,
                success=True,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                data=[],
                total_count=0,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
```

### QuickBooks Platform Implementation
```python
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks

class QuickBooksPlatform(BasePlatform):
    """QuickBooks platform implementation"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials, PlatformType.ACCOUNTING)
        self.qb = None
        self.auth_client = None
    
    async def connect(self) -> bool:
        """Connect to QuickBooks using OAuth2"""
        try:
            self.auth_client = AuthClient(
                client_id=self.credentials.api_key,
                client_secret=self.credentials.password,
                environment=self.credentials.environment,
                redirect_uri='http://localhost:8000/callback'
            )
            
            # In production, would handle OAuth flow properly
            # For now, assume we have valid tokens
            self.qb = QuickBooks(
                auth_client=self.auth_client,
                refresh_token=self.credentials.security_token,
                company_id=self.credentials.instance_url
            )
            
            self.is_connected = True
            return True
        except Exception as e:
            print(f"QuickBooks connection failed: {e}")
            return False
    
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute QuickBooks query"""
        start_time = time.time()
        try:
            # QuickBooks uses different query syntax
            if 'SELECT' in query.upper():
                # SQL-like query
                result = self.qb.query(query)
            else:
                # Entity-based query
                entity_type = self._extract_entity_type(query)
                result = getattr(self.qb, entity_type).query(query)
            
            data = result if isinstance(result, list) else [result]
            total_count = len(data)
            
            execution_time = time.time() - start_time
            return QueryResult(
                data=data,
                total_count=total_count,
                success=True,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                data=[],
                total_count=0,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _extract_entity_type(self, query: str) -> str:
        """Extract entity type from QuickBooks query"""
        # Simplified extraction
        if 'Invoice' in query:
            return 'invoices'
        elif 'Customer' in query:
            return 'customers'
        elif 'Item' in query:
            return 'items'
        return 'customers'  # Default
```

## Platform Factory and Registry

### Platform Factory
```python
class PlatformFactory:
    """Factory for creating platform instances"""
    
    _platforms = {
        'salesforce': SalesforcePlatform,
        'servicenow': ServiceNowPlatform,
        'netsuite': NetSuitePlatform,
        'quickbooks': QuickBooksPlatform
    }
    
    @classmethod
    def create_platform(cls, platform_name: str, credentials: PlatformCredentials) -> BasePlatform:
        """Create a platform instance"""
        if platform_name.lower() not in cls._platforms:
            raise ValueError(f"Unsupported platform: {platform_name}")
        
        platform_class = cls._platforms[platform_name.lower()]
        return platform_class(credentials)
    
    @classmethod
    def register_platform(cls, name: str, platform_class: type):
        """Register a new platform implementation"""
        cls._platforms[name.lower()] = platform_class
    
    @classmethod
    def get_supported_platforms(cls) -> List[str]:
        """Get list of supported platforms"""
        return list(cls._platforms.keys())
```

### Platform Registry
```python
class PlatformRegistry:
    """Registry for managing platform connections"""
    
    def __init__(self):
        self.platforms: Dict[str, BasePlatform] = {}
        self.credentials: Dict[str, PlatformCredentials] = {}
    
    async def register_platform(self, name: str, credentials: PlatformCredentials) -> bool:
        """Register and connect to a platform"""
        try:
            platform = PlatformFactory.create_platform(name, credentials)
            success = await platform.connect()
            
            if success:
                self.platforms[name] = platform
                self.credentials[name] = credentials
                return True
            return False
        except Exception as e:
            print(f"Failed to register platform {name}: {e}")
            return False
    
    async def get_platform(self, name: str) -> Optional[BasePlatform]:
        """Get platform instance"""
        return self.platforms.get(name)
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all registered platforms"""
        results = {}
        for name, platform in self.platforms.items():
            results[name] = await platform.health_check()
        return results
    
    async def disconnect_all(self):
        """Disconnect from all platforms"""
        for platform in self.platforms.values():
            await platform.disconnect()
        self.platforms.clear()
        self.credentials.clear()
```

## Configuration Management

### Platform Configuration Schema
```yaml
# platform_config.yaml
platforms:
  salesforce:
    type: "crm"
    api_version: "v58.0"
    environment: "sandbox"  # production, sandbox
    credentials:
      username: "${SALESFORCE_USERNAME}"
      password: "${SALESFORCE_PASSWORD}"
      security_token: "${SALESFORCE_SECURITY_TOKEN}"
    connection_pool:
      max_connections: 10
      timeout: 30
  
  servicenow:
    type: "itsm"
    instance: "${SERVICENOW_INSTANCE}"
    api_version: "v2"
    credentials:
      username: "${SERVICENOW_USERNAME}"
      password: "${SERVICENOW_PASSWORD}"
    connection_pool:
      max_connections: 5
      timeout: 60
  
  netsuite:
    type: "erp"
    environment: "sandbox"  # production, sandbox
    credentials:
      account_id: "${NETSUITE_ACCOUNT_ID}"
      consumer_key: "${NETSUITE_CONSUMER_KEY}"
      consumer_secret: "${NETSUITE_CONSUMER_SECRET}"
      token_id: "${NETSUITE_TOKEN_ID}"
      token_secret: "${NETSUITE_TOKEN_SECRET}"
  
  quickbooks:
    type: "accounting"
    environment: "sandbox"  # production, sandbox
    credentials:
      client_id: "${QB_CLIENT_ID}"
      client_secret: "${QB_CLIENT_SECRET}"
      company_id: "${QB_COMPANY_ID}"
      refresh_token: "${QB_REFRESH_TOKEN}"
```

### Configuration Loader
```python
import yaml
import os
from typing import Dict, Any

class PlatformConfigLoader:
    """Load and manage platform configurations"""
    
    def __init__(self, config_path: str = "platform_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    def get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """Get configuration for a specific platform"""
        return self.config.get('platforms', {}).get(platform_name, {})
    
    def create_credentials(self, platform_name: str) -> PlatformCredentials:
        """Create credentials object from configuration"""
        platform_config = self.get_platform_config(platform_name)
        creds_config = platform_config.get('credentials', {})
        
        # Resolve environment variables
        resolved_creds = {}
        for key, value in creds_config.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                resolved_creds[key] = os.getenv(env_var, '')
            else:
                resolved_creds[key] = value
        
        return PlatformCredentials(
            username=resolved_creds.get('username', ''),
            password=resolved_creds.get('password', ''),
            api_key=resolved_creds.get('api_key'),
            security_token=resolved_creds.get('security_token'),
            instance_url=resolved_creds.get('instance_url') or resolved_creds.get('instance'),
            environment=platform_config.get('environment', 'production')
        )
```

This platform abstraction layer provides a robust foundation for integrating multiple enterprise software platforms while maintaining consistency and extensibility across the EnterpriseArena framework.
