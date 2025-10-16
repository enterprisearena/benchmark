"""
QuickBooks Tools

This module provides QuickBooks-specific tools and utilities for EnterpriseArena.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QuickBooksTools:
    """
    QuickBooks-specific tools and utilities.
    
    This class provides high-level tools for common QuickBooks operations,
    making it easier to perform complex tasks without dealing with low-level API calls.
    """
    
    def __init__(self, connector, schema_manager):
        """
        Initialize QuickBooks tools.
        
        Args:
            connector: QuickBooksConnector instance
            schema_manager: QuickBooksSchema instance
        """
        self.connector = connector
        self.schema = schema_manager
    
    async def find_customer_by_name(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a customer by name.
        
        Args:
            customer_name: Name of the customer to find
            
        Returns:
            Customer record if found, None otherwise
        """
        try:
            criteria = {"Name": customer_name}
            result = await self.connector.search_records("Customer", criteria)
            
            if result.success and result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find customer by name {customer_name}: {e}")
            raise
    
    async def find_customers_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Find customers by status.
        
        Args:
            status: Status to filter by (e.g., 'Active', 'Inactive')
            
        Returns:
            List of customer records
        """
        try:
            criteria = {"Active": "true" if status == "Active" else "false"}
            result = await self.connector.search_records("Customer", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find customers by status {status}: {e}")
            raise
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer.
        
        Args:
            customer_data: Data for the new customer
            
        Returns:
            Creation result
        """
        try:
            # Validate customer data
            validation_result = await self.schema.validate_field_data("Customer", customer_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid customer data: {validation_result['errors']}")
            
            result = await self.connector.create_record("Customer", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            raise
    
    async def find_invoices_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Find invoices for a specific customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            List of invoice records
        """
        try:
            criteria = {"CustomerRef": customer_id}
            result = await self.connector.search_records("Invoice", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find invoices for customer {customer_id}: {e}")
            raise
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new invoice.
        
        Args:
            invoice_data: Data for the new invoice
            
        Returns:
            Creation result
        """
        try:
            # Validate invoice data
            validation_result = await self.schema.validate_field_data("Invoice", invoice_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid invoice data: {validation_result['errors']}")
            
            result = await self.connector.create_record("Invoice", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            raise
    
    async def find_vendors_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Find vendors by status.
        
        Args:
            status: Status to filter by (e.g., 'Active', 'Inactive')
            
        Returns:
            List of vendor records
        """
        try:
            criteria = {"Active": "true" if status == "Active" else "false"}
            result = await self.connector.search_records("Vendor", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find vendors by status {status}: {e}")
            raise
    
    async def create_vendor(self, vendor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new vendor.
        
        Args:
            vendor_data: Data for the new vendor
            
        Returns:
            Creation result
        """
        try:
            # Validate vendor data
            validation_result = await self.schema.validate_field_data("Vendor", vendor_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid vendor data: {validation_result['errors']}")
            
            result = await self.connector.create_record("Vendor", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create vendor: {e}")
            raise
    
    async def find_bills_by_vendor(self, vendor_id: str) -> List[Dict[str, Any]]:
        """
        Find bills for a specific vendor.
        
        Args:
            vendor_id: ID of the vendor
            
        Returns:
            List of bill records
        """
        try:
            criteria = {"VendorRef": vendor_id}
            result = await self.connector.search_records("Bill", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find bills for vendor {vendor_id}: {e}")
            raise
    
    async def create_bill(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new bill.
        
        Args:
            bill_data: Data for the new bill
            
        Returns:
            Creation result
        """
        try:
            # Validate bill data
            validation_result = await self.schema.validate_field_data("Bill", bill_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid bill data: {validation_result['errors']}")
            
            result = await self.connector.create_record("Bill", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create bill: {e}")
            raise
    
    async def find_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """
        Find items by type.
        
        Args:
            item_type: Type of item to search for (e.g., 'Inventory', 'Service', 'NonInventory')
            
        Returns:
            List of item records
        """
        try:
            criteria = {"Type": item_type}
            result = await self.connector.search_records("Item", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find items by type {item_type}: {e}")
            raise
    
    async def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new item.
        
        Args:
            item_data: Data for the new item
            
        Returns:
            Creation result
        """
        try:
            # Validate item data
            validation_result = await self.schema.validate_field_data("Item", item_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid item data: {validation_result['errors']}")
            
            result = await self.connector.create_record("Item", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create item: {e}")
            raise
    
    async def get_financial_summary(self, customer_id: str) -> Dict[str, Any]:
        """
        Get financial summary for a customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Dict containing financial summary
        """
        try:
            # Get customer info
            customer = await self.find_customer_by_name(customer_id)
            if not customer:
                return {"error": "Customer not found"}
            
            # Get invoices
            invoices = await self.find_invoices_by_customer(customer_id)
            
            # Calculate totals
            total_invoices = len(invoices)
            total_amount = sum(float(invoice.get("TotalAmt", 0)) for invoice in invoices)
            
            return {
                "customer_id": customer_id,
                "customer_name": customer.get("Name", "Unknown"),
                "total_invoices": total_invoices,
                "total_amount": total_amount
            }
            
        except Exception as e:
            logger.error(f"Failed to get financial summary for customer {customer_id}: {e}")
            raise
    
    async def get_recent_transactions(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent transactions.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent transaction records
        """
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Query for recent invoices
            invoices_query = f"""
                SELECT * FROM Invoice 
                WHERE TxnDate >= '{start_date}'
                ORDER BY TxnDate DESC
                MAXRESULTS 50
            """
            
            result = await self.connector.execute_query(invoices_query)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get recent transactions: {e}")
            raise
