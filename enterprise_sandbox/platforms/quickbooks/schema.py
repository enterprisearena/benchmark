"""
QuickBooks Schema Management

This module provides schema management functionality for QuickBooks entities.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class QuickBooksSchema:
    """
    QuickBooks schema management class.
    
    This class provides methods for working with QuickBooks entity schemas,
    including field definitions, relationships, and validation rules.
    """
    
    def __init__(self, connector):
        """
        Initialize QuickBooks schema manager.
        
        Args:
            connector: QuickBooksConnector instance
        """
        self.connector = connector
        self._schema_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 3600  # 1 hour cache TTL
    
    async def get_entity_schema(self, entity_type: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get schema for a specific QuickBooks entity type.
        
        Args:
            entity_type: Name of the QuickBooks entity type
            use_cache: Whether to use cached schema if available
            
        Returns:
            Dict containing entity schema information
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            cached_schema = self._schema_cache.get(entity_type)
            if cached_schema:
                logger.debug(f"Using cached schema for {entity_type}")
                return cached_schema
        
        try:
            # Get schema from QuickBooks
            schema_data = await self.connector.get_schema(entity_type)
            
            # Process and cache the schema
            processed_schema = self._process_entity_schema(schema_data, entity_type)
            
            if use_cache:
                self._schema_cache[entity_type] = processed_schema
                self._cache_timestamp = datetime.now()
            
            return processed_schema
            
        except Exception as e:
            logger.error(f"Failed to get schema for {entity_type}: {e}")
            raise
    
    async def get_all_entity_types(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get list of all available QuickBooks entity types.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            List of entity type information dictionaries
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            cached_types = self._schema_cache.get("__all_entity_types__")
            if cached_types:
                logger.debug("Using cached entity type list")
                return cached_types
        
        try:
            # Get company info as reference
            schema_data = await self.connector.get_schema()
            
            # Process entity type list
            entity_types = []
            for item in schema_data.get("QueryResponse", {}).get("CompanyInfo", []):
                entity_types.append({
                    "name": "CompanyInfo",
                    "label": "Company Information",
                    "type": "company",
                    "description": "Company information and settings"
                })
            
            if use_cache:
                self._schema_cache["__all_entity_types__"] = entity_types
                self._cache_timestamp = datetime.now()
            
            return entity_types
            
        except Exception as e:
            logger.error(f"Failed to get entity type list: {e}")
            raise
    
    async def get_common_entity_types(self) -> List[str]:
        """
        Get list of common QuickBooks entity types.
        
        Returns:
            List of common entity type names
        """
        return [
            "Customer",
            "Vendor", 
            "Employee",
            "Item",
            "Invoice",
            "Payment",
            "Bill",
            "Purchase",
            "SalesReceipt",
            "Estimate",
            "CreditMemo",
            "RefundReceipt",
            "JournalEntry",
            "Account",
            "TaxCode",
            "TaxRate",
            "Class",
            "Department",
            "Location",
            "Currency",
            "Term",
            "PaymentMethod",
            "ShipMethod",
            "CompanyInfo",
            "Preferences",
            "Attachable",
            "Budget",
            "CashFlow",
            "Report",
            "TimeActivity",
            "Transfer",
            "VendorCredit",
            "Deposit",
            "PurchaseOrder",
            "SalesOrder",
            "ItemReceipt",
            "InventoryAdjustment",
            "InventoryTransfer",
            "AssemblyItem",
            "NonInventoryItem",
            "ServiceItem",
            "OtherChargeItem",
            "DiscountItem",
            "TaxItem",
            "GroupItem",
            "SubtotalItem",
            "PaymentItem",
            "CreditCardPayment",
            "Check",
            "CreditCardCredit",
            "Deposit",
            "Transfer",
            "JournalEntry",
            "GeneralDetail",
            "Line",
            "LinkedTxn",
            "TxnTaxDetail",
            "TxnTaxCodeRef",
            "CustomField",
            "CustomFieldDefinition",
            "AttachableRef",
            "MetaData",
            "SyncToken",
            "Id",
            "Sparse",
            "domain",
            "status",
            "Fault",
            "Error"
        ]
    
    async def validate_field_data(self, entity_type: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate field data against entity schema.
        
        Args:
            entity_type: Name of the QuickBooks entity type
            field_data: Data to validate
            
        Returns:
            Dict containing validation results
        """
        try:
            entity_schema = await self.get_entity_schema(entity_type)
            fields = {field["name"]: field for field in entity_schema.get("fields", [])}
            
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
                    
                    validation_results["validated_data"][field_name] = field_value
                else:
                    validation_results["warnings"].append(f"Unknown field {field_name}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate field data for {entity_type}: {e}")
            raise
    
    def _process_entity_schema(self, schema_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Process raw schema data into a more usable format.
        
        Args:
            schema_data: Raw schema data from QuickBooks
            entity_type: Name of the entity type
            
        Returns:
            Processed schema data
        """
        processed = {
            "name": entity_type,
            "label": entity_type.replace("_", " ").title(),
            "type": "entity",
            "fields": [],
            "description": f"QuickBooks {entity_type} entity"
        }
        
        # Process fields from the schema data
        if "QueryResponse" in schema_data:
            entity_data = schema_data["QueryResponse"].get(entity_type, [])
            if entity_data and not isinstance(entity_data, list):
                entity_data = [entity_data]
            
            if entity_data:
                # Extract field information from the first entity
                sample_entity = entity_data[0]
                for field_name, field_value in sample_entity.items():
                    processed_field = {
                        "name": field_name,
                        "label": field_name.replace("_", " ").title(),
                        "type": self._infer_field_type(field_value),
                        "mandatory": False,  # QuickBooks doesn't provide this info easily
                        "read_only": False,
                        "description": f"{field_name} field"
                    }
                    processed["fields"].append(processed_field)
        
        return processed
    
    def _infer_field_type(self, value: Any) -> str:
        """
        Infer field type from sample value.
        
        Args:
            value: Sample field value
            
        Returns:
            str: Inferred field type
        """
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"
    
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
            "array": list,
            "object": dict
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
            "cached_entity_types": list(self._schema_cache.keys()),
            "cache_size": len(self._schema_cache),
            "cache_timestamp": self._cache_timestamp,
            "cache_ttl": self._cache_ttl,
            "cache_valid": self._is_cache_valid()
        }
