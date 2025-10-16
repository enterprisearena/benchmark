"""
Salesforce Schema Management

This module provides schema management functionality for Salesforce objects.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SalesforceSchema:
    """
    Salesforce schema management class.
    
    This class provides methods for working with Salesforce object schemas,
    including field definitions, relationships, and validation rules.
    """
    
    def __init__(self, connector):
        """
        Initialize Salesforce schema manager.
        
        Args:
            connector: SalesforceConnector instance
        """
        self.connector = connector
        self._schema_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 3600  # 1 hour cache TTL
    
    async def get_object_schema(self, object_type: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get schema for a specific Salesforce object.
        
        Args:
            object_type: Type of Salesforce object
            use_cache: Whether to use cached schema if available
            
        Returns:
            Dict containing object schema information
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            cached_schema = self._schema_cache.get(object_type)
            if cached_schema:
                logger.debug(f"Using cached schema for {object_type}")
                return cached_schema
        
        try:
            # Get schema from Salesforce
            schema_data = await self.connector.get_schema(object_type)
            
            # Process and cache the schema
            processed_schema = self._process_object_schema(schema_data)
            
            if use_cache:
                self._schema_cache[object_type] = processed_schema
                self._cache_timestamp = datetime.now()
            
            return processed_schema
            
        except Exception as e:
            logger.error(f"Failed to get schema for {object_type}: {e}")
            raise
    
    async def get_all_objects(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get list of all available Salesforce objects.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            List of object information dictionaries
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            cached_objects = self._schema_cache.get("__all_objects__")
            if cached_objects:
                logger.debug("Using cached object list")
                return cached_objects
        
        try:
            # Get global schema from Salesforce
            schema_data = await self.connector.get_schema()
            
            # Process object list
            objects = []
            for sobject in schema_data.get("sobjects", []):
                objects.append({
                    "name": sobject.get("name"),
                    "label": sobject.get("label"),
                    "labelPlural": sobject.get("labelPlural"),
                    "custom": sobject.get("custom", False),
                    "createable": sobject.get("createable", False),
                    "updateable": sobject.get("updateable", False),
                    "deletable": sobject.get("deletable", False),
                    "queryable": sobject.get("queryable", False),
                    "searchable": sobject.get("searchable", False),
                    "retrieveable": sobject.get("retrieveable", False),
                    "undeletable": sobject.get("undeletable", False),
                    "mergeable": sobject.get("mergeable", False),
                    "replicateable": sobject.get("replicateable", False),
                    "triggerable": sobject.get("triggerable", False),
                    "deprecatedAndHidden": sobject.get("deprecatedAndHidden", False)
                })
            
            if use_cache:
                self._schema_cache["__all_objects__"] = objects
                self._cache_timestamp = datetime.now()
            
            return objects
            
        except Exception as e:
            logger.error(f"Failed to get object list: {e}")
            raise
    
    async def get_field_schema(self, object_type: str, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get schema for a specific field in an object.
        
        Args:
            object_type: Type of Salesforce object
            field_name: Name of the field
            
        Returns:
            Dict containing field schema information, or None if not found
        """
        try:
            object_schema = await self.get_object_schema(object_type)
            fields = object_schema.get("fields", [])
            
            for field in fields:
                if field.get("name") == field_name:
                    return field
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get field schema for {object_type}.{field_name}: {e}")
            raise
    
    async def get_relationship_schema(self, object_type: str) -> List[Dict[str, Any]]:
        """
        Get relationship information for an object.
        
        Args:
            object_type: Type of Salesforce object
            
        Returns:
            List of relationship information dictionaries
        """
        try:
            object_schema = await self.get_object_schema(object_type)
            return object_schema.get("childRelationships", [])
            
        except Exception as e:
            logger.error(f"Failed to get relationship schema for {object_type}: {e}")
            raise
    
    async def validate_field_data(self, object_type: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate field data against object schema.
        
        Args:
            object_type: Type of Salesforce object
            field_data: Data to validate
            
        Returns:
            Dict containing validation results
        """
        try:
            object_schema = await self.get_object_schema(object_type)
            fields = {field["name"]: field for field in object_schema.get("fields", [])}
            
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "validated_data": {}
            }
            
            for field_name, field_value in field_data.items():
                if field_name in fields:
                    field_schema = fields[field_name]
                    
                    # Check if field is required
                    if field_schema.get("nillable", True) is False and field_value is None:
                        validation_results["errors"].append(f"Required field {field_name} is missing")
                        validation_results["valid"] = False
                    
                    # Check field type
                    field_type = field_schema.get("type")
                    if field_type and not self._validate_field_type(field_value, field_type):
                        validation_results["warnings"].append(
                            f"Field {field_name} value may not match expected type {field_type}"
                        )
                    
                    # Check field length
                    if field_schema.get("length") and isinstance(field_value, str):
                        if len(field_value) > field_schema["length"]:
                            validation_results["errors"].append(
                                f"Field {field_name} exceeds maximum length of {field_schema['length']}"
                            )
                            validation_results["valid"] = False
                    
                    validation_results["validated_data"][field_name] = field_value
                else:
                    validation_results["warnings"].append(f"Unknown field {field_name}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate field data for {object_type}: {e}")
            raise
    
    def _process_object_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw schema data into a more usable format.
        
        Args:
            schema_data: Raw schema data from Salesforce
            
        Returns:
            Processed schema data
        """
        processed = {
            "name": schema_data.get("name"),
            "label": schema_data.get("label"),
            "labelPlural": schema_data.get("labelPlural"),
            "custom": schema_data.get("custom", False),
            "fields": [],
            "childRelationships": schema_data.get("childRelationships", []),
            "recordTypeInfos": schema_data.get("recordTypeInfos", []),
            "supportedScopes": schema_data.get("supportedScopes", []),
            "createable": schema_data.get("createable", False),
            "updateable": schema_data.get("updateable", False),
            "deletable": schema_data.get("deletable", False),
            "queryable": schema_data.get("queryable", False),
            "searchable": schema_data.get("searchable", False),
            "retrieveable": schema_data.get("retrieveable", False)
        }
        
        # Process fields
        for field in schema_data.get("fields", []):
            processed_field = {
                "name": field.get("name"),
                "label": field.get("label"),
                "type": field.get("type"),
                "length": field.get("length"),
                "precision": field.get("precision"),
                "scale": field.get("scale"),
                "nillable": field.get("nillable", True),
                "unique": field.get("unique", False),
                "caseSensitive": field.get("caseSensitive", False),
                "defaultedOnCreate": field.get("defaultedOnCreate", False),
                "calculated": field.get("calculated", False),
                "createable": field.get("createable", False),
                "updateable": field.get("updateable", False),
                "filterable": field.get("filterable", False),
                "sortable": field.get("sortable", False),
                "groupable": field.get("groupable", False),
                "custom": field.get("custom", False),
                "referenceTo": field.get("referenceTo", []),
                "relationshipName": field.get("relationshipName"),
                "picklistValues": field.get("picklistValues", [])
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
            return True  # Null values are handled by nillable check
        
        type_mapping = {
            "string": str,
            "textarea": str,
            "email": str,
            "url": str,
            "phone": str,
            "int": int,
            "double": (int, float),
            "currency": (int, float),
            "percent": (int, float),
            "boolean": bool,
            "date": str,  # Salesforce dates are strings
            "datetime": str,  # Salesforce datetimes are strings
            "time": str,  # Salesforce times are strings
            "id": str,
            "reference": str,
            "picklist": str,
            "multipicklist": str,
            "address": str,
            "location": str,
            "base64": str
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
            "cached_objects": list(self._schema_cache.keys()),
            "cache_size": len(self._schema_cache),
            "cache_timestamp": self._cache_timestamp,
            "cache_ttl": self._cache_ttl,
            "cache_valid": self._is_cache_valid()
        }
