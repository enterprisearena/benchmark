"""
Salesforce Tools

This module provides Salesforce-specific tools and utilities for EnterpriseArena.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SalesforceTools:
    """
    Salesforce-specific tools and utilities.
    
    This class provides high-level tools for common Salesforce operations,
    making it easier to perform complex tasks without dealing with low-level API calls.
    """
    
    def __init__(self, connector, schema_manager):
        """
        Initialize Salesforce tools.
        
        Args:
            connector: SalesforceConnector instance
            schema_manager: SalesforceSchema instance
        """
        self.connector = connector
        self.schema = schema_manager
    
    async def find_account_by_name(self, account_name: str) -> Optional[Dict[str, Any]]:
        """
        Find an account by name.
        
        Args:
            account_name: Name of the account to find
            
        Returns:
            Account record if found, None otherwise
        """
        try:
            criteria = {"Name": account_name}
            result = await self.connector.search_records("Account", criteria)
            
            if result.success and result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find account by name {account_name}: {e}")
            raise
    
    async def find_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a contact by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Contact record if found, None otherwise
        """
        try:
            criteria = {"Email": email}
            result = await self.connector.search_records("Contact", criteria)
            
            if result.success and result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find contact by email {email}: {e}")
            raise
    
    async def find_lead_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a lead by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Lead record if found, None otherwise
        """
        try:
            criteria = {"Email": email}
            result = await self.connector.search_records("Lead", criteria)
            
            if result.success and result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find lead by email {email}: {e}")
            raise
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new lead.
        
        Args:
            lead_data: Data for the new lead
            
        Returns:
            Creation result
        """
        try:
            # Validate lead data
            validation_result = await self.schema.validate_field_data("Lead", lead_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid lead data: {validation_result['errors']}")
            
            result = await self.connector.create_record("Lead", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create lead: {e}")
            raise
    
    async def convert_lead_to_opportunity(self, lead_id: str, opportunity_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert a lead to an opportunity.
        
        Args:
            lead_id: ID of the lead to convert
            opportunity_data: Additional data for the opportunity
            
        Returns:
            Conversion result
        """
        try:
            # Get lead information
            lead_query = f"SELECT Id, FirstName, LastName, Email, Company, Phone FROM Lead WHERE Id = '{lead_id}'"
            lead_result = await self.connector.execute_query(lead_query)
            
            if not lead_result.success or not lead_result.data:
                raise ValueError(f"Lead with ID {lead_id} not found")
            
            lead = lead_result.data[0]
            
            # Prepare opportunity data
            opp_data = {
                "Name": f"{lead.get('FirstName', '')} {lead.get('LastName', '')} - {lead.get('Company', '')}".strip(),
                "StageName": "Prospecting",
                "CloseDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "LeadSource": "Web"
            }
            
            # Add any additional opportunity data
            if opportunity_data:
                opp_data.update(opportunity_data)
            
            # Create opportunity
            opp_result = await self.connector.create_record("Opportunity", opp_data)
            
            if opp_result.success:
                # Update lead status to converted
                await self.connector.update_record("Lead", lead_id, {"Status": "Converted"})
            
            return opp_result
            
        except Exception as e:
            logger.error(f"Failed to convert lead {lead_id} to opportunity: {e}")
            raise
    
    async def get_recent_leads(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get leads created in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent lead records
        """
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            query = f"SELECT Id, FirstName, LastName, Email, Company, Status, CreatedDate FROM Lead WHERE CreatedDate >= {start_date} ORDER BY CreatedDate DESC"
            
            result = await self.connector.execute_query(query)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get recent leads: {e}")
            raise
    
    async def get_opportunities_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """
        Get opportunities by stage.
        
        Args:
            stage: Opportunity stage to filter by
            
        Returns:
            List of opportunity records
        """
        try:
            criteria = {"StageName": stage}
            result = await self.connector.search_records("Opportunity", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get opportunities by stage {stage}: {e}")
            raise
    
    async def get_account_contacts(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all contacts for an account.
        
        Args:
            account_id: ID of the account
            
        Returns:
            List of contact records
        """
        try:
            criteria = {"AccountId": account_id}
            result = await self.connector.search_records("Contact", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get contacts for account {account_id}: {e}")
            raise
    
    async def get_account_opportunities(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all opportunities for an account.
        
        Args:
            account_id: ID of the account
            
        Returns:
            List of opportunity records
        """
        try:
            criteria = {"AccountId": account_id}
            result = await self.connector.search_records("Opportunity", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get opportunities for account {account_id}: {e}")
            raise
    
    async def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new case.
        
        Args:
            case_data: Data for the new case
            
        Returns:
            Creation result
        """
        try:
            # Validate case data
            validation_result = await self.schema.validate_field_data("Case", case_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid case data: {validation_result['errors']}")
            
            result = await self.connector.create_record("Case", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create case: {e}")
            raise
    
    async def update_case_status(self, case_id: str, status: str) -> Dict[str, Any]:
        """
        Update case status.
        
        Args:
            case_id: ID of the case to update
            status: New status for the case
            
        Returns:
            Update result
        """
        try:
            result = await self.connector.update_record("Case", case_id, {"Status": status})
            return result
            
        except Exception as e:
            logger.error(f"Failed to update case status: {e}")
            raise
    
    async def get_cases_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get cases by status.
        
        Args:
            status: Case status to filter by
            
        Returns:
            List of case records
        """
        try:
            criteria = {"Status": status}
            result = await self.connector.search_records("Case", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get cases by status {status}: {e}")
            raise
    
    async def search_records_by_text(self, object_type: str, search_text: str, fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search records using SOSL (Salesforce Object Search Language).
        
        Args:
            object_type: Type of object to search
            search_text: Text to search for
            fields: Fields to return (defaults to Id, Name)
            
        Returns:
            List of matching records
        """
        try:
            if fields is None:
                fields = ["Id", "Name"]
            
            fields_str = ", ".join(fields)
            sosl_query = f"FIND {{{search_text}}} IN ALL FIELDS RETURNING {object_type}({fields_str})"
            
            # Note: This would need to be implemented in the connector for SOSL support
            # For now, fall back to SOQL search on Name field
            criteria = {"Name": search_text}
            result = await self.connector.search_records(object_type, criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to search {object_type} records: {e}")
            raise
    
    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user information.
        
        Returns:
            User information dictionary
        """
        try:
            query = "SELECT Id, Name, Email, Username, UserRole.Name, Profile.Name FROM User WHERE Id = $User.Id"
            result = await self.connector.execute_query(query)
            
            if result.success and result.data:
                return result.data[0]
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise
    
    async def get_organization_info(self) -> Dict[str, Any]:
        """
        Get organization information.
        
        Returns:
            Organization information dictionary
        """
        try:
            query = "SELECT Id, Name, OrganizationType, Industry, Phone, Website FROM Organization LIMIT 1"
            result = await self.connector.execute_query(query)
            
            if result.success and result.data:
                return result.data[0]
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get organization info: {e}")
            raise
