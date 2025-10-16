"""
Environment Utilities

This module provides utility functions and classes for environment implementations.
"""

import logging
import json
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class EnvironmentUtils:
    """Utility class for environment operations."""
    
    @staticmethod
    def validate_task_structure(task: Dict[str, Any]) -> bool:
        """
        Validate task structure and required fields.
        
        Args:
            task: Task dictionary to validate
            
        Returns:
            bool: True if valid, raises ValueError if invalid
        """
        required_fields = ["task", "answer"]
        
        for field in required_fields:
            if field not in task:
                raise ValueError(f"Task missing required field: {field}")
        
        # Validate task content
        if not task["task"] or not isinstance(task["task"], str):
            raise ValueError("Task field must be a non-empty string")
        
        # Validate answer format
        answer = task["answer"]
        if not isinstance(answer, (str, list, dict)):
            raise ValueError("Answer field must be a string, list, or dictionary")
        
        return True
    
    @staticmethod
    def parse_natural_language_query(query: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured format.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dict containing parsed query information
        """
        query_lower = query.lower()
        
        # Extract action type
        action_type = "query"  # default
        if any(word in query_lower for word in ["find", "search", "get", "retrieve", "show"]):
            action_type = "query"
        elif any(word in query_lower for word in ["create", "add", "new", "insert"]):
            action_type = "create"
        elif any(word in query_lower for word in ["update", "modify", "change", "edit"]):
            action_type = "update"
        elif any(word in query_lower for word in ["delete", "remove", "destroy"]):
            action_type = "delete"
        
        # Extract object type
        object_type = None
        object_patterns = {
            "lead": ["lead", "leads"],
            "account": ["account", "accounts", "company", "companies"],
            "contact": ["contact", "contacts", "person", "people"],
            "opportunity": ["opportunity", "opportunities", "deal", "deals"],
            "case": ["case", "cases", "ticket", "tickets"],
            "user": ["user", "users", "person", "people"]
        }
        
        for obj_type, patterns in object_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                object_type = obj_type
                break
        
        # Extract filters/criteria
        filters = {}
        
        # Look for specific field filters
        if "email" in query_lower:
            email_match = re.search(r'email[:\s]+([^\s]+)', query_lower)
            if email_match:
                filters["Email"] = email_match.group(1)
        
        if "name" in query_lower:
            name_match = re.search(r'name[:\s]+([^\s]+)', query_lower)
            if name_match:
                filters["Name"] = name_match.group(1)
        
        if "status" in query_lower:
            status_match = re.search(r'status[:\s]+([^\s]+)', query_lower)
            if status_match:
                filters["Status"] = status_match.group(1)
        
        # Extract time-based filters
        if "last" in query_lower and "days" in query_lower:
            days_match = re.search(r'last[:\s]+(\d+)[:\s]+days?', query_lower)
            if days_match:
                filters["created_last_days"] = int(days_match.group(1))
        
        return {
            "action_type": action_type,
            "object_type": object_type,
            "filters": filters,
            "original_query": query
        }
    
    @staticmethod
    def format_platform_response(response: Any, platform: str) -> str:
        """
        Format platform response for consistent display.
        
        Args:
            response: Platform response
            platform: Platform name
            
        Returns:
            str: Formatted response string
        """
        if isinstance(response, dict):
            if response.get("success", False):
                data = response.get("data", [])
                if isinstance(data, list):
                    if data:
                        return f"{platform.title()} returned {len(data)} records"
                    else:
                        return f"{platform.title()} returned no records"
                elif isinstance(data, dict):
                    return f"{platform.title()} operation successful"
                else:
                    return f"{platform.title()} operation completed"
            else:
                error = response.get("error_message", "Unknown error")
                return f"{platform.title()} error: {error}"
        elif isinstance(response, str):
            return f"{platform.title()}: {response}"
        else:
            return f"{platform.title()}: {str(response)}"
    
    @staticmethod
    def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate evaluation metrics from results.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Dict containing calculated metrics
        """
        if not results:
            return {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "success_rate": 0.0,
                "average_reward": 0.0,
                "average_execution_time": 0.0
            }
        
        total_tasks = len(results)
        successful_tasks = sum(1 for r in results if r.get("success", False))
        failed_tasks = total_tasks - successful_tasks
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0
        
        rewards = [r.get("reward", 0.0) for r in results]
        average_reward = sum(rewards) / len(rewards) if rewards else 0.0
        
        execution_times = [r.get("execution_time", 0.0) for r in results]
        average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": success_rate,
            "average_reward": average_reward,
            "average_execution_time": average_execution_time
        }
    
    @staticmethod
    def generate_report(results: List[Dict[str, Any]], output_file: str):
        """
        Generate comprehensive evaluation report.
        
        Args:
            results: List of evaluation results
            output_file: Path to output file
        """
        try:
            metrics = EnvironmentUtils.calculate_metrics(results)
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "summary": metrics,
                "detailed_results": results
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Report generated: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    @staticmethod
    def extract_platform_from_task(task: Dict[str, Any]) -> Optional[str]:
        """
        Extract platform information from task.
        
        Args:
            task: Task dictionary
            
        Returns:
            str: Platform name if found, None otherwise
        """
        # Check explicit platform field
        if "platform" in task:
            return task["platform"]
        
        # Check platforms field (for cross-platform tasks)
        if "platforms" in task and isinstance(task["platforms"], list):
            return task["platforms"][0] if task["platforms"] else None
        
        # Infer from task content
        task_text = task.get("task", "").lower()
        
        if "salesforce" in task_text:
            return "salesforce"
        elif "servicenow" in task_text:
            return "servicenow"
        elif "netsuite" in task_text:
            return "netsuite"
        elif "quickbooks" in task_text:
            return "quickbooks"
        
        return None
    
    @staticmethod
    def validate_environment_config(config: Dict[str, Any]) -> bool:
        """
        Validate environment configuration.
        
        Args:
            config: Environment configuration dictionary
            
        Returns:
            bool: True if valid, raises ValueError if invalid
        """
        required_fields = ["environment_type"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Environment config missing required field: {field}")
        
        # Validate environment type
        valid_types = ["single_platform", "cross_platform", "interactive", "chat", "tool"]
        if config["environment_type"] not in valid_types:
            raise ValueError(f"Invalid environment type: {config['environment_type']}")
        
        # Validate platform-specific config
        if config["environment_type"] == "single_platform":
            if "platform" not in config:
                raise ValueError("Single platform environment requires 'platform' field")
        
        elif config["environment_type"] == "cross_platform":
            if "platforms" not in config or not isinstance(config["platforms"], list):
                raise ValueError("Cross platform environment requires 'platforms' list")
        
        return True
    
    @staticmethod
    def create_environment_id(config: Dict[str, Any]) -> str:
        """
        Create a unique ID for an environment configuration.
        
        Args:
            config: Environment configuration
            
        Returns:
            str: Unique environment ID
        """
        # Create a hash of the configuration
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"env_{timestamp}_{config_hash}"
    
    @staticmethod
    def format_execution_time(seconds: float) -> str:
        """
        Format execution time for display.
        
        Args:
            seconds: Execution time in seconds
            
        Returns:
            str: Formatted time string
        """
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def sanitize_task_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize task data for safe processing.
        
        Args:
            data: Task data to sanitize
            
        Returns:
            Dict: Sanitized task data
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potentially harmful characters
                sanitized_value = re.sub(r'[<>"\']', '', value)
                sanitized[key] = sanitized_value
            elif isinstance(value, (dict, list)):
                # Recursively sanitize nested structures
                sanitized[key] = EnvironmentUtils.sanitize_task_data(value) if isinstance(value, dict) else value
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def compare_results(expected: Any, actual: Any) -> Dict[str, Any]:
        """
        Compare expected and actual results.
        
        Args:
            expected: Expected result
            actual: Actual result
            
        Returns:
            Dict containing comparison results
        """
        comparison = {
            "exact_match": expected == actual,
            "type_match": type(expected) == type(actual),
            "similarity_score": 0.0
        }
        
        # Calculate similarity score
        if isinstance(expected, str) and isinstance(actual, str):
            # Simple string similarity
            if expected.lower() == actual.lower():
                comparison["similarity_score"] = 1.0
            elif expected.lower() in actual.lower() or actual.lower() in expected.lower():
                comparison["similarity_score"] = 0.5
        elif isinstance(expected, list) and isinstance(actual, list):
            # List similarity
            if len(expected) == len(actual):
                matches = sum(1 for e, a in zip(expected, actual) if e == a)
                comparison["similarity_score"] = matches / len(expected) if expected else 0.0
        
        return comparison
