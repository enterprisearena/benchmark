"""
Platform Utilities

This module provides utility functions and classes for platform implementations.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import hashlib
import secrets

logger = logging.getLogger(__name__)


class PlatformUtils:
    """Utility class for platform operations."""
    
    @staticmethod
    def validate_credentials(credentials: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that all required credential fields are present.
        
        Args:
            credentials: Credentials dictionary to validate
            required_fields: List of required field names
            
        Returns:
            bool: True if all required fields are present, False otherwise
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"Missing required credential fields: {missing_fields}")
            return False
        
        return True
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """
        Sanitize query string to prevent injection attacks.
        
        Args:
            query: Query string to sanitize
            
        Returns:
            str: Sanitized query string
        """
        # Remove potentially dangerous characters
        dangerous_patterns = [
            r'--.*',  # SQL comments
            r'/\*.*?\*/',  # SQL block comments
            r';\s*drop\s+',  # DROP statements
            r';\s*delete\s+',  # DELETE statements
            r';\s*insert\s+',  # INSERT statements
            r';\s*update\s+',  # UPDATE statements
        ]
        
        sanitized_query = query
        for pattern in dangerous_patterns:
            sanitized_query = re.sub(pattern, '', sanitized_query, flags=re.IGNORECASE)
        
        return sanitized_query.strip()
    
    @staticmethod
    def format_response_data(data: Any, max_items: int = 100) -> List[Dict[str, Any]]:
        """
        Format response data for consistent output.
        
        Args:
            data: Raw response data
            max_items: Maximum number of items to return
            
        Returns:
            List of formatted data dictionaries
        """
        if not data:
            return []
        
        # Handle different data types
        if isinstance(data, list):
            formatted_data = data[:max_items]
        elif isinstance(data, dict):
            formatted_data = [data]
        else:
            # Convert other types to string representation
            formatted_data = [{"value": str(data)}]
        
        # Ensure all items are dictionaries
        result = []
        for item in formatted_data:
            if isinstance(item, dict):
                result.append(item)
            else:
                result.append({"value": str(item)})
        
        return result
    
    @staticmethod
    def calculate_execution_time(start_time: datetime) -> float:
        """
        Calculate execution time in seconds.
        
        Args:
            start_time: Start time of the operation
            
        Returns:
            float: Execution time in seconds
        """
        return (datetime.now() - start_time).total_seconds()
    
    @staticmethod
    def generate_request_id() -> str:
        """
        Generate a unique request ID for tracking.
        
        Returns:
            str: Unique request ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = secrets.token_hex(4)
        return f"req_{timestamp}_{random_suffix}"
    
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict[str, Any]:
        """
        Mask sensitive data in dictionaries for logging.
        
        Args:
            data: Dictionary containing potentially sensitive data
            sensitive_fields: List of field names to mask
            
        Returns:
            Dict with sensitive fields masked
        """
        if sensitive_fields is None:
            sensitive_fields = [
                'password', 'token', 'secret', 'key', 'credential',
                'auth', 'login', 'passwd', 'pwd', 'api_key'
            ]
        
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive_field in key.lower() for sensitive_field in sensitive_fields):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                else:
                    masked_data[key] = "***"
        
        return masked_data
    
    @staticmethod
    def parse_error_message(error: Union[str, Exception]) -> str:
        """
        Parse error message from various error types.
        
        Args:
            error: Error string or exception object
            
        Returns:
            str: Parsed error message
        """
        if isinstance(error, Exception):
            return str(error)
        elif isinstance(error, str):
            return error
        else:
            return f"Unknown error: {error}"
    
    @staticmethod
    def validate_object_type(object_type: str, allowed_types: List[str]) -> bool:
        """
        Validate that object type is in allowed list.
        
        Args:
            object_type: Object type to validate
            allowed_types: List of allowed object types
            
        Returns:
            bool: True if object type is allowed, False otherwise
        """
        return object_type.lower() in [t.lower() for t in allowed_types]
    
    @staticmethod
    def normalize_field_name(field_name: str) -> str:
        """
        Normalize field names for consistent handling.
        
        Args:
            field_name: Field name to normalize
            
        Returns:
            str: Normalized field name
        """
        # Convert to lowercase and replace spaces with underscores
        normalized = re.sub(r'[^a-zA-Z0-9_]', '_', field_name.lower())
        # Remove multiple consecutive underscores
        normalized = re.sub(r'_+', '_', normalized)
        # Remove leading/trailing underscores
        return normalized.strip('_')
    
    @staticmethod
    def build_where_clause(criteria: Dict[str, Any]) -> str:
        """
        Build WHERE clause from criteria dictionary.
        
        Args:
            criteria: Dictionary of field-value pairs for filtering
            
        Returns:
            str: WHERE clause string
        """
        if not criteria:
            return ""
        
        conditions = []
        for field, value in criteria.items():
            if isinstance(value, str):
                conditions.append(f"{field} = '{value}'")
            elif isinstance(value, (int, float)):
                conditions.append(f"{field} = {value}")
            elif isinstance(value, list):
                if value:
                    value_list = "', '".join(str(v) for v in value)
                    conditions.append(f"{field} IN ('{value_list}')")
            else:
                conditions.append(f"{field} = '{str(value)}'")
        
        return " AND ".join(conditions)
    
    @staticmethod
    def extract_record_id(response: Dict[str, Any], id_fields: List[str] = None) -> Optional[str]:
        """
        Extract record ID from platform response.
        
        Args:
            response: Platform response dictionary
            id_fields: List of possible ID field names
            
        Returns:
            str: Record ID if found, None otherwise
        """
        if id_fields is None:
            id_fields = ['id', 'Id', 'ID', 'record_id', 'RecordId', 'RECORD_ID']
        
        for field in id_fields:
            if field in response:
                return str(response[field])
        
        # Look for nested ID fields
        for key, value in response.items():
            if isinstance(value, dict):
                nested_id = PlatformUtils.extract_record_id(value, id_fields)
                if nested_id:
                    return nested_id
        
        return None
    
    @staticmethod
    def create_error_result(error_message: str, execution_time: float = 0.0) -> Dict[str, Any]:
        """
        Create standardized error result.
        
        Args:
            error_message: Error message
            execution_time: Execution time in seconds
            
        Returns:
            Dict: Standardized error result
        """
        return {
            "success": False,
            "error_message": error_message,
            "execution_time": execution_time,
            "data": None,
            "total_count": 0
        }
    
    @staticmethod
    def create_success_result(data: Any, execution_time: float = 0.0, total_count: int = None) -> Dict[str, Any]:
        """
        Create standardized success result.
        
        Args:
            data: Result data
            execution_time: Execution time in seconds
            total_count: Total number of records
            
        Returns:
            Dict: Standardized success result
        """
        formatted_data = PlatformUtils.format_response_data(data)
        
        return {
            "success": True,
            "data": formatted_data,
            "execution_time": execution_time,
            "total_count": total_count or len(formatted_data),
            "error_message": None
        }
