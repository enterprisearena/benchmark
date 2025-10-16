"""
NetSuite Tools

This module provides NetSuite-specific tools and utilities for EnterpriseArena.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NetSuiteTools:
    """
    NetSuite-specific tools and utilities.
    
    This class provides high-level tools for common NetSuite operations,
    making it easier to perform complex tasks without dealing with low-level API calls.
    """
    
    def __init__(self, connector, schema_manager):
        """
        Initialize NetSuite tools.
        
        Args:
            connector: NetSuiteConnector instance
            schema_manager: NetSuiteSchema instance
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
            criteria = {"entityid": customer_name}
            result = await self.connector.search_records("customer", criteria)
            
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
            criteria = {"isinactive": "F" if status == "Active" else "T"}
            result = await self.connector.search_records("customer", criteria)
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
            validation_result = await self.schema.validate_field_data("customer", customer_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid customer data: {validation_result['errors']}")
            
            result = await self.connector.create_record("customer", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            raise
    
    async def update_customer_status(self, customer_id: str, status: str) -> Dict[str, Any]:
        """
        Update customer status.
        
        Args:
            customer_id: Internal ID of the customer to update
            status: New status for the customer
            
        Returns:
            Update result
        """
        try:
            isinactive = "T" if status == "Inactive" else "F"
            result = await self.connector.update_record("customer", customer_id, {"isinactive": isinactive})
            return result
            
        except Exception as e:
            logger.error(f"Failed to update customer status: {e}")
            raise
    
    async def find_sales_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Find sales orders for a specific customer.
        
        Args:
            customer_id: Internal ID of the customer
            
        Returns:
            List of sales order records
        """
        try:
            criteria = {"entity": customer_id}
            result = await self.connector.search_records("salesorder", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find sales orders for customer {customer_id}: {e}")
            raise
    
    async def create_sales_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new sales order.
        
        Args:
            order_data: Data for the new sales order
            
        Returns:
            Creation result
        """
        try:
            # Validate sales order data
            validation_result = await self.schema.validate_field_data("salesorder", order_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid sales order data: {validation_result['errors']}")
            
            result = await self.connector.create_record("salesorder", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create sales order: {e}")
            raise
    
    async def find_invoices_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Find invoices for a specific customer.
        
        Args:
            customer_id: Internal ID of the customer
            
        Returns:
            List of invoice records
        """
        try:
            criteria = {"entity": customer_id}
            result = await self.connector.search_records("invoice", criteria)
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
            validation_result = await self.schema.validate_field_data("invoice", invoice_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid invoice data: {validation_result['errors']}")
            
            result = await self.connector.create_record("invoice", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            raise
    
    async def find_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """
        Find items by type.
        
        Args:
            item_type: Type of item to search for (e.g., 'InvtPart', 'Service', 'NonInvtPart')
            
        Returns:
            List of item records
        """
        try:
            criteria = {"type": item_type}
            result = await self.connector.search_records("item", criteria)
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
            validation_result = await self.schema.validate_field_data("item", item_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid item data: {validation_result['errors']}")
            
            result = await self.connector.create_record("item", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create item: {e}")
            raise
    
    async def find_employees_by_department(self, department_id: str) -> List[Dict[str, Any]]:
        """
        Find employees by department.
        
        Args:
            department_id: Internal ID of the department
            
        Returns:
            List of employee records
        """
        try:
            criteria = {"department": department_id}
            result = await self.connector.search_records("employee", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find employees by department {department_id}: {e}")
            raise
    
    async def create_employee(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new employee.
        
        Args:
            employee_data: Data for the new employee
            
        Returns:
            Creation result
        """
        try:
            # Validate employee data
            validation_result = await self.schema.validate_field_data("employee", employee_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid employee data: {validation_result['errors']}")
            
            result = await self.connector.create_record("employee", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create employee: {e}")
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
            criteria = {"isinactive": "F" if status == "Active" else "T"}
            result = await self.connector.search_records("vendor", criteria)
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
            validation_result = await self.schema.validate_field_data("vendor", vendor_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid vendor data: {validation_result['errors']}")
            
            result = await self.connector.create_record("vendor", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create vendor: {e}")
            raise
    
    async def find_purchase_orders_by_vendor(self, vendor_id: str) -> List[Dict[str, Any]]:
        """
        Find purchase orders for a specific vendor.
        
        Args:
            vendor_id: Internal ID of the vendor
            
        Returns:
            List of purchase order records
        """
        try:
            criteria = {"entity": vendor_id}
            result = await self.connector.search_records("purchaseorder", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find purchase orders for vendor {vendor_id}: {e}")
            raise
    
    async def create_purchase_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new purchase order.
        
        Args:
            order_data: Data for the new purchase order
            
        Returns:
            Creation result
        """
        try:
            # Validate purchase order data
            validation_result = await self.schema.validate_field_data("purchaseorder", order_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid purchase order data: {validation_result['errors']}")
            
            result = await self.connector.create_record("purchaseorder", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create purchase order: {e}")
            raise
    
    async def get_financial_summary(self, customer_id: str) -> Dict[str, Any]:
        """
        Get financial summary for a customer.
        
        Args:
            customer_id: Internal ID of the customer
            
        Returns:
            Dict containing financial summary
        """
        try:
            # Get customer info
            customer = await self.find_customer_by_name(customer_id)
            if not customer:
                return {"error": "Customer not found"}
            
            # Get sales orders
            sales_orders = await self.find_sales_orders_by_customer(customer_id)
            
            # Get invoices
            invoices = await self.find_invoices_by_customer(customer_id)
            
            # Calculate totals
            total_sales = sum(float(order.get("total", 0)) for order in sales_orders)
            total_invoices = sum(float(invoice.get("total", 0)) for invoice in invoices)
            
            return {
                "customer_id": customer_id,
                "customer_name": customer.get("entityid", "Unknown"),
                "total_sales_orders": len(sales_orders),
                "total_sales_amount": total_sales,
                "total_invoices": len(invoices),
                "total_invoice_amount": total_invoices,
                "outstanding_balance": total_invoices - total_sales  # Simplified calculation
            }
            
        except Exception as e:
            logger.error(f"Failed to get financial summary for customer {customer_id}: {e}")
            raise
    
    async def get_inventory_summary(self) -> Dict[str, Any]:
        """
        Get inventory summary.
        
        Returns:
            Dict containing inventory summary
        """
        try:
            # Get inventory items
            inventory_items = await self.find_items_by_type("InvtPart")
            
            # Calculate summary
            total_items = len(inventory_items)
            active_items = sum(1 for item in inventory_items if not item.get("isinactive", False))
            
            return {
                "total_inventory_items": total_items,
                "active_items": active_items,
                "inactive_items": total_items - active_items
            }
            
        except Exception as e:
            logger.error(f"Failed to get inventory summary: {e}")
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
            
            # Query for recent sales orders
            sales_orders_query = f"""
                SELECT id, entity, total, trandate, status
                FROM salesorder 
                WHERE trandate >= '{start_date}'
                ORDER BY trandate DESC
                LIMIT 50
            """
            
            result = await self.connector.execute_query(sales_orders_query)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get recent transactions: {e}")
            raise
