"""
ServiceNow Tools

This module provides ServiceNow-specific tools and utilities for EnterpriseArena.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ServiceNowTools:
    """
    ServiceNow-specific tools and utilities.
    
    This class provides high-level tools for common ServiceNow operations,
    making it easier to perform complex tasks without dealing with low-level API calls.
    """
    
    def __init__(self, connector, schema_manager):
        """
        Initialize ServiceNow tools.
        
        Args:
            connector: ServiceNowConnector instance
            schema_manager: ServiceNowSchema instance
        """
        self.connector = connector
        self.schema = schema_manager
    
    async def find_incident_by_number(self, incident_number: str) -> Optional[Dict[str, Any]]:
        """
        Find an incident by number.
        
        Args:
            incident_number: Number of the incident to find
            
        Returns:
            Incident record if found, None otherwise
        """
        try:
            criteria = {"number": incident_number}
            result = await self.connector.search_records("incident", criteria)
            
            if result.success and result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find incident by number {incident_number}: {e}")
            raise
    
    async def find_incidents_by_state(self, state: str) -> List[Dict[str, Any]]:
        """
        Find incidents by state.
        
        Args:
            state: State to filter by (e.g., 'New', 'In Progress', 'Resolved')
            
        Returns:
            List of incident records
        """
        try:
            criteria = {"state": state}
            result = await self.connector.search_records("incident", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find incidents by state {state}: {e}")
            raise
    
    async def find_incidents_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """
        Find incidents by priority.
        
        Args:
            priority: Priority to filter by (e.g., '1 - Critical', '2 - High')
            
        Returns:
            List of incident records
        """
        try:
            criteria = {"priority": priority}
            result = await self.connector.search_records("incident", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to find incidents by priority {priority}: {e}")
            raise
    
    async def create_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new incident.
        
        Args:
            incident_data: Data for the new incident
            
        Returns:
            Creation result
        """
        try:
            # Validate incident data
            validation_result = await self.schema.validate_field_data("incident", incident_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid incident data: {validation_result['errors']}")
            
            result = await self.connector.create_record("incident", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create incident: {e}")
            raise
    
    async def update_incident_state(self, incident_sys_id: str, state: str) -> Dict[str, Any]:
        """
        Update incident state.
        
        Args:
            incident_sys_id: Sys ID of the incident to update
            state: New state for the incident
            
        Returns:
            Update result
        """
        try:
            result = await self.connector.update_record("incident", incident_sys_id, {"state": state})
            return result
            
        except Exception as e:
            logger.error(f"Failed to update incident state: {e}")
            raise
    
    async def assign_incident(self, incident_sys_id: str, assigned_to: str) -> Dict[str, Any]:
        """
        Assign an incident to a user.
        
        Args:
            incident_sys_id: Sys ID of the incident to assign
            assigned_to: Sys ID of the user to assign to
            
        Returns:
            Update result
        """
        try:
            result = await self.connector.update_record("incident", incident_sys_id, {
                "assigned_to": assigned_to,
                "state": "Assigned"
            })
            return result
            
        except Exception as e:
            logger.error(f"Failed to assign incident: {e}")
            raise
    
    async def get_recent_incidents(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get incidents created in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent incident records
        """
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            parameters = {
                "sysparm_query": f"sys_created_on>={start_date}",
                "sysparm_order_by": "sys_created_on desc"
            }
            
            result = await self.connector.execute_query("incident", parameters)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get recent incidents: {e}")
            raise
    
    async def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User record if found, None otherwise
        """
        try:
            criteria = {"email": email}
            result = await self.connector.search_records("sys_user", criteria)
            
            if result.success and result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
            raise
    
    async def find_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by name.
        
        Args:
            name: Name to search for
            
        Returns:
            User record if found, None otherwise
        """
        try:
            criteria = {"name": name}
            result = await self.connector.search_records("sys_user", criteria)
            
            if result.success and result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find user by name {name}: {e}")
            raise
    
    async def get_user_groups(self, user_sys_id: str) -> List[Dict[str, Any]]:
        """
        Get groups for a user.
        
        Args:
            user_sys_id: Sys ID of the user
            
        Returns:
            List of group records
        """
        try:
            parameters = {
                "sysparm_query": f"user={user_sys_id}",
                "sysparm_display_value": "true"
            }
            
            result = await self.connector.execute_query("sys_user_grmember", parameters)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get user groups: {e}")
            raise
    
    async def create_change_request(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new change request.
        
        Args:
            change_data: Data for the new change request
            
        Returns:
            Creation result
        """
        try:
            # Validate change request data
            validation_result = await self.schema.validate_field_data("change_request", change_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid change request data: {validation_result['errors']}")
            
            result = await self.connector.create_record("change_request", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create change request: {e}")
            raise
    
    async def get_change_request_tasks(self, change_sys_id: str) -> List[Dict[str, Any]]:
        """
        Get tasks for a change request.
        
        Args:
            change_sys_id: Sys ID of the change request
            
        Returns:
            List of change task records
        """
        try:
            criteria = {"change_request": change_sys_id}
            result = await self.connector.search_records("change_task", criteria)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get change request tasks: {e}")
            raise
    
    async def create_problem(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new problem.
        
        Args:
            problem_data: Data for the new problem
            
        Returns:
            Creation result
        """
        try:
            # Validate problem data
            validation_result = await self.schema.validate_field_data("problem", problem_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid problem data: {validation_result['errors']}")
            
            result = await self.connector.create_record("problem", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create problem: {e}")
            raise
    
    async def link_incident_to_problem(self, incident_sys_id: str, problem_sys_id: str) -> Dict[str, Any]:
        """
        Link an incident to a problem.
        
        Args:
            incident_sys_id: Sys ID of the incident
            problem_sys_id: Sys ID of the problem
            
        Returns:
            Update result
        """
        try:
            result = await self.connector.update_record("incident", incident_sys_id, {
                "problem_id": problem_sys_id
            })
            return result
            
        except Exception as e:
            logger.error(f"Failed to link incident to problem: {e}")
            raise
    
    async def search_knowledge_base(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of knowledge base articles
        """
        try:
            parameters = {
                "sysparm_query": f"textCONTAINS{search_term}",
                "sysparm_display_value": "true"
            }
            
            result = await self.connector.execute_query("kb_knowledge", parameters)
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to search knowledge base: {e}")
            raise
    
    async def get_configuration_items(self, ci_type: str = None) -> List[Dict[str, Any]]:
        """
        Get configuration items.
        
        Args:
            ci_type: Optional CI type to filter by
            
        Returns:
            List of configuration item records
        """
        try:
            if ci_type:
                criteria = {"sys_class_name": ci_type}
                result = await self.connector.search_records("cmdb_ci", criteria)
            else:
                result = await self.connector.execute_query("cmdb_ci", {"sysparm_limit": 100})
            
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get configuration items: {e}")
            raise
    
    async def get_service_catalog_items(self) -> List[Dict[str, Any]]:
        """
        Get service catalog items.
        
        Returns:
            List of service catalog item records
        """
        try:
            result = await self.connector.execute_query("sc_cat_item", {"sysparm_limit": 100})
            return result.data if result.success else []
            
        except Exception as e:
            logger.error(f"Failed to get service catalog items: {e}")
            raise
    
    async def create_service_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new service request.
        
        Args:
            request_data: Data for the new service request
            
        Returns:
            Creation result
        """
        try:
            # Validate service request data
            validation_result = await self.schema.validate_field_data("sc_request", request_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid service request data: {validation_result['errors']}")
            
            result = await self.connector.create_record("sc_request", validation_result["validated_data"])
            return result
            
        except Exception as e:
            logger.error(f"Failed to create service request: {e}")
            raise
    
    async def get_incident_statistics(self) -> Dict[str, Any]:
        """
        Get incident statistics.
        
        Returns:
            Dict containing incident statistics
        """
        try:
            # Get total incidents
            total_result = await self.connector.execute_query("incident", {"sysparm_limit": 1})
            total_count = total_result.total_count if total_result.success else 0
            
            # Get incidents by state
            states = ["New", "In Progress", "Resolved", "Closed"]
            state_counts = {}
            
            for state in states:
                criteria = {"state": state}
                result = await self.connector.search_records("incident", criteria)
                state_counts[state] = len(result.data) if result.success else 0
            
            return {
                "total_incidents": total_count,
                "by_state": state_counts
            }
            
        except Exception as e:
            logger.error(f"Failed to get incident statistics: {e}")
            raise
