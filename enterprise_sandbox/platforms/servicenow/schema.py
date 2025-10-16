"""
ServiceNow Schema Management

This module provides schema management functionality for ServiceNow tables.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ServiceNowSchema:
    """
    ServiceNow schema management class.
    
    This class provides methods for working with ServiceNow table schemas,
    including field definitions, relationships, and validation rules.
    """
    
    def __init__(self, connector):
        """
        Initialize ServiceNow schema manager.
        
        Args:
            connector: ServiceNowConnector instance
        """
        self.connector = connector
        self._schema_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 3600  # 1 hour cache TTL
    
    async def get_table_schema(self, table_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get schema for a specific ServiceNow table.
        
        Args:
            table_name: Name of the ServiceNow table
            use_cache: Whether to use cached schema if available
            
        Returns:
            Dict containing table schema information
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            cached_schema = self._schema_cache.get(table_name)
            if cached_schema:
                logger.debug(f"Using cached schema for {table_name}")
                return cached_schema
        
        try:
            # Get schema from ServiceNow
            schema_data = await self.connector.get_schema(table_name)
            
            # Process and cache the schema
            processed_schema = self._process_table_schema(schema_data, table_name)
            
            if use_cache:
                self._schema_cache[table_name] = processed_schema
                self._cache_timestamp = datetime.now()
            
            return processed_schema
            
        except Exception as e:
            logger.error(f"Failed to get schema for {table_name}: {e}")
            raise
    
    async def get_all_tables(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get list of all available ServiceNow tables.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            List of table information dictionaries
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            cached_tables = self._schema_cache.get("__all_tables__")
            if cached_tables:
                logger.debug("Using cached table list")
                return cached_tables
        
        try:
            # Get global schema from ServiceNow
            schema_data = await self.connector.get_schema()
            
            # Process table list
            tables = []
            for table_info in schema_data.get("result", []):
                tables.append({
                    "name": table_info.get("name"),
                    "label": table_info.get("label"),
                    "sys_name": table_info.get("sys_name"),
                    "sys_class_name": table_info.get("sys_class_name"),
                    "sys_package": table_info.get("sys_package"),
                    "sys_scope": table_info.get("sys_scope"),
                    "active": table_info.get("active", True),
                    "read_only": table_info.get("read_only", False),
                    "sys_created_on": table_info.get("sys_created_on"),
                    "sys_updated_on": table_info.get("sys_updated_on")
                })
            
            if use_cache:
                self._schema_cache["__all_tables__"] = tables
                self._cache_timestamp = datetime.now()
            
            return tables
            
        except Exception as e:
            logger.error(f"Failed to get table list: {e}")
            raise
    
    async def get_field_schema(self, table_name: str, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get schema for a specific field in a table.
        
        Args:
            table_name: Name of the ServiceNow table
            field_name: Name of the field
            
        Returns:
            Dict containing field schema information, or None if not found
        """
        try:
            table_schema = await self.get_table_schema(table_name)
            fields = table_schema.get("fields", [])
            
            for field in fields:
                if field.get("name") == field_name:
                    return field
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get field schema for {table_name}.{field_name}: {e}")
            raise
    
    async def get_common_tables(self) -> List[str]:
        """
        Get list of common ServiceNow tables.
        
        Returns:
            List of common table names
        """
        return [
            "incident",
            "problem", 
            "change_request",
            "change_task",
            "sc_request",
            "sc_req_item",
            "sc_task",
            "sys_user",
            "sys_user_group",
            "cmdb_ci",
            "cmdb_rel_ci",
            "kb_knowledge",
            "sys_script",
            "sys_ui_page",
            "sys_ui_action",
            "sys_ui_list",
            "sys_ui_section",
            "sys_ui_related_list",
            "sys_ui_related_list_action",
            "sys_ui_related_list_action_script"
        ]
    
    async def validate_field_data(self, table_name: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate field data against table schema.
        
        Args:
            table_name: Name of the ServiceNow table
            field_data: Data to validate
            
        Returns:
            Dict containing validation results
        """
        try:
            table_schema = await self.get_table_schema(table_name)
            fields = {field["name"]: field for field in table_schema.get("fields", [])}
            
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "validated_data": {}
            }
            
            for field_name, field_value in field_data.items():
                if field_name in fields:
                    field_schema = fields[field_name]
                    
                    # Check if field is mandatory
                    if field_schema.get("mandatory", False) and (field_value is None or field_value == ""):
                        validation_results["errors"].append(f"Mandatory field {field_name} is missing")
                        validation_results["valid"] = False
                    
                    # Check field type
                    field_type = field_schema.get("type")
                    if field_type and not self._validate_field_type(field_value, field_type):
                        validation_results["warnings"].append(
                            f"Field {field_name} value may not match expected type {field_type}"
                        )
                    
                    # Check field length
                    if field_schema.get("max_length") and isinstance(field_value, str):
                        if len(field_value) > field_schema["max_length"]:
                            validation_results["errors"].append(
                                f"Field {field_name} exceeds maximum length of {field_schema['max_length']}"
                            )
                            validation_results["valid"] = False
                    
                    validation_results["validated_data"][field_name] = field_value
                else:
                    validation_results["warnings"].append(f"Unknown field {field_name}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate field data for {table_name}: {e}")
            raise
    
    def _process_table_schema(self, schema_data: Dict[str, Any], table_name: str) -> Dict[str, Any]:
        """
        Process raw schema data into a more usable format.
        
        Args:
            schema_data: Raw schema data from ServiceNow
            table_name: Name of the table
            
        Returns:
            Processed schema data
        """
        processed = {
            "name": table_name,
            "label": schema_data.get("label", table_name),
            "sys_name": schema_data.get("sys_name", table_name),
            "sys_class_name": schema_data.get("sys_class_name"),
            "fields": [],
            "relationships": schema_data.get("relationships", []),
            "indexes": schema_data.get("indexes", []),
            "active": schema_data.get("active", True),
            "read_only": schema_data.get("read_only", False)
        }
        
        # Process fields from the result data
        result_data = schema_data.get("result", [])
        if isinstance(result_data, list) and result_data:
            # If result is a list, it contains field information
            for field in result_data:
                processed_field = {
                    "name": field.get("name"),
                    "label": field.get("label"),
                    "type": field.get("type"),
                    "max_length": field.get("max_length"),
                    "mandatory": field.get("mandatory", False),
                    "read_only": field.get("read_only", False),
                    "default_value": field.get("default_value"),
                    "reference": field.get("reference"),
                    "choice_table": field.get("choice_table"),
                    "choice_field": field.get("choice_field"),
                    "dependent_on_field": field.get("dependent_on_field"),
                    "sys_created_on": field.get("sys_created_on"),
                    "sys_updated_on": field.get("sys_updated_on")
                }
                processed["fields"].append(processed_field)
        else:
            # If result is not a list, it might be table metadata
            processed["description"] = schema_data.get("description", "")
            processed["sys_created_on"] = schema_data.get("sys_created_on")
            processed["sys_updated_on"] = schema_data.get("sys_updated_on")
        
        return processed
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """
        Validate that a value matches the expected field type.
        
        Args:
            value: Value to validate
            expected_type: Expected field type
            
        Returns:
            bool: True if value matches expected type, False otherwise
        """
        if value is None:
            return True  # Null values are handled by mandatory check
        
        type_mapping = {
            "string": str,
            "integer": int,
            "decimal": (int, float),
            "boolean": bool,
            "date": str,  # ServiceNow dates are strings
            "datetime": str,  # ServiceNow datetimes are strings
            "time": str,  # ServiceNow times are strings
            "glide_date": str,
            "glide_date_time": str,
            "glide_time": str,
            "glide_duration": str,
            "reference": str,
            "choice": str,
            "journal": str,
            "journal_input": str,
            "password": str,
            "script": str,
            "translated_text": str,
            "translated_html": str,
            "url": str,
            "email": str,
            "phone_number": str,
            "currency": (int, float),
            "percent": (int, float)
        }
        
        expected_python_type = type_mapping.get(expected_type.lower())
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Unknown types are assumed valid
    
    def _is_cache_valid(self) -> bool:
        """
        Check if the schema cache is still valid.
        
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if not self._cache_timestamp:
            return False
        
        cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
        return cache_age < self._cache_ttl
    
    def clear_cache(self):
        """Clear the schema cache."""
        self._schema_cache.clear()
        self._cache_timestamp = None
        logger.info("Schema cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the current cache state.
        
        Returns:
            Dict containing cache information
        """
        return {
            "cached_tables": list(self._schema_cache.keys()),
            "cache_size": len(self._schema_cache),
            "cache_timestamp": self._cache_timestamp,
            "cache_ttl": self._cache_ttl,
            "cache_valid": self._is_cache_valid()
        }
