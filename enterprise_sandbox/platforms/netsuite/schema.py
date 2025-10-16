"""
NetSuite Schema Management

This module provides schema management functionality for NetSuite records.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NetSuiteSchema:
    """
    NetSuite schema management class.
    
    This class provides methods for working with NetSuite record schemas,
    including field definitions, relationships, and validation rules.
    """
    
    def __init__(self, connector):
        """
        Initialize NetSuite schema manager.
        
        Args:
            connector: NetSuiteConnector instance
        """
        self.connector = connector
        self._schema_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 3600  # 1 hour cache TTL
    
    async def get_record_schema(self, record_type: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get schema for a specific NetSuite record type.
        
        Args:
            record_type: Name of the NetSuite record type
            use_cache: Whether to use cached schema if available
            
        Returns:
            Dict containing record schema information
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            cached_schema = self._schema_cache.get(record_type)
            if cached_schema:
                logger.debug(f"Using cached schema for {record_type}")
                return cached_schema
        
        try:
            # Get schema from NetSuite
            schema_data = await self.connector.get_schema(record_type)
            
            # Process and cache the schema
            processed_schema = self._process_record_schema(schema_data, record_type)
            
            if use_cache:
                self._schema_cache[record_type] = processed_schema
                self._cache_timestamp = datetime.now()
            
            return processed_schema
            
        except Exception as e:
            logger.error(f"Failed to get schema for {record_type}: {e}")
            raise
    
    async def get_all_record_types(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get list of all available NetSuite record types.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            List of record type information dictionaries
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            cached_types = self._schema_cache.get("__all_record_types__")
            if cached_types:
                logger.debug("Using cached record type list")
                return cached_types
        
        try:
            # Get metadata catalog from NetSuite
            schema_data = await self.connector.get_schema()
            
            # Process record type list
            record_types = []
            for item in schema_data.get("items", []):
                record_types.append({
                    "name": item.get("name"),
                    "label": item.get("label"),
                    "type": item.get("type"),
                    "is_custom": item.get("isCustom", False),
                    "is_inactive": item.get("isInactive", False),
                    "url": item.get("url"),
                    "fields_url": item.get("fieldsUrl")
                })
            
            if use_cache:
                self._schema_cache["__all_record_types__"] = record_types
                self._cache_timestamp = datetime.now()
            
            return record_types
            
        except Exception as e:
            logger.error(f"Failed to get record type list: {e}")
            raise
    
    async def get_field_schema(self, record_type: str, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get schema for a specific field in a record type.
        
        Args:
            record_type: Name of the NetSuite record type
            field_name: Name of the field
            
        Returns:
            Dict containing field schema information, or None if not found
        """
        try:
            record_schema = await self.get_record_schema(record_type)
            fields = record_schema.get("fields", [])
            
            for field in fields:
                if field.get("name") == field_name:
                    return field
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get field schema for {record_type}.{field_name}: {e}")
            raise
    
    async def get_common_record_types(self) -> List[str]:
        """
        Get list of common NetSuite record types.
        
        Returns:
            List of common record type names
        """
        return [
            "customer",
            "vendor", 
            "employee",
            "item",
            "salesorder",
            "purchaseorder",
            "invoice",
            "creditmemo",
            "estimate",
            "cashsale",
            "journalentry",
            "account",
            "subsidiary",
            "department",
            "class",
            "location",
            "currency",
            "taxitem",
            "paymentmethod",
            "customercategory",
            "vendorcategory",
            "itemcategory",
            "contact",
            "contactrole",
            "address",
            "phonecall",
            "task",
            "event",
            "note",
            "file",
            "folder",
            "customlist",
            "customrecord",
            "workflow",
            "script",
            "savedsearch",
            "report",
            "dashboard",
            "kpi",
            "suitelet",
            "restlet",
            "scheduledscript",
            "mapreducescript",
            "massupdatescript",
            "usereventscript",
            "clientscript",
            "portlet",
            "form",
            "transactionbodycustomfield",
            "transactioncolumncustomfield",
            "entitycustomfield",
            "itemcustomfield",
            "othercustomfield",
            "crmcustomfield"
        ]
    
    async def validate_field_data(self, record_type: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate field data against record schema.
        
        Args:
            record_type: Name of the NetSuite record type
            field_data: Data to validate
            
        Returns:
            Dict containing validation results
        """
        try:
            record_schema = await self.get_record_schema(record_type)
            fields = {field["name"]: field for field in record_schema.get("fields", [])}
            
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
                    if field_schema.get("maxLength") and isinstance(field_value, str):
                        if len(field_value) > field_schema["maxLength"]:
                            validation_results["errors"].append(
                                f"Field {field_name} exceeds maximum length of {field_schema['maxLength']}"
                            )
                            validation_results["valid"] = False
                    
                    validation_results["validated_data"][field_name] = field_value
                else:
                    validation_results["warnings"].append(f"Unknown field {field_name}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate field data for {record_type}: {e}")
            raise
    
    def _process_record_schema(self, schema_data: Dict[str, Any], record_type: str) -> Dict[str, Any]:
        """
        Process raw schema data into a more usable format.
        
        Args:
            schema_data: Raw schema data from NetSuite
            record_type: Name of the record type
            
        Returns:
            Processed schema data
        """
        processed = {
            "name": record_type,
            "label": schema_data.get("label", record_type),
            "type": schema_data.get("type", "customrecord"),
            "is_custom": schema_data.get("isCustom", False),
            "is_inactive": schema_data.get("isInactive", False),
            "fields": [],
            "sublists": schema_data.get("sublists", []),
            "url": schema_data.get("url"),
            "fields_url": schema_data.get("fieldsUrl")
        }
        
        # Process fields from the schema data
        fields_data = schema_data.get("fields", [])
        if isinstance(fields_data, list):
            for field in fields_data:
                processed_field = {
                    "name": field.get("name"),
                    "label": field.get("label"),
                    "type": field.get("type"),
                    "mandatory": field.get("mandatory", False),
                    "read_only": field.get("readOnly", False),
                    "max_length": field.get("maxLength"),
                    "default_value": field.get("defaultValue"),
                    "select_options": field.get("selectOptions", []),
                    "reference": field.get("reference"),
                    "is_custom": field.get("isCustom", False),
                    "is_inactive": field.get("isInactive", False),
                    "help": field.get("help"),
                    "validation": field.get("validation")
                }
                processed["fields"].append(processed_field)
        
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
            "float": float,
            "boolean": bool,
            "date": str,  # NetSuite dates are strings
            "datetime": str,  # NetSuite datetimes are strings
            "time": str,  # NetSuite times are strings
            "currency": (int, float),
            "percent": (int, float),
            "select": str,
            "multiselect": list,
            "reference": str,
            "text": str,
            "longtext": str,
            "rich": str,
            "email": str,
            "url": str,
            "phone": str,
            "checkbox": bool,
            "freeformtext": str,
            "integer": int,
            "currency": (int, float),
            "percent": (int, float),
            "file": str,
            "image": str
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
            "cached_record_types": list(self._schema_cache.keys()),
            "cache_size": len(self._schema_cache),
            "cache_timestamp": self._cache_timestamp,
            "cache_ttl": self._cache_ttl,
            "cache_valid": self._is_cache_valid()
        }
