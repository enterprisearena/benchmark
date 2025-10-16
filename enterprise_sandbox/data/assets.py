"""
EnterpriseArena Data Assets

This module loads and provides access to all task definitions for EnterpriseArena,
including single-platform and cross-platform tasks.
"""

from .tasks.single_platform.salesforce_tasks import (
    SALESFORCE_TASKS, 
    SALESFORCE_INTERACTIVE_TASKS
)
from .tasks.single_platform.servicenow_tasks import (
    SERVICENOW_TASKS, 
    SERVICENOW_INTERACTIVE_TASKS
)
from .tasks.cross_platform.financial_integration import (
    FINANCIAL_INTEGRATION_TASKS,
    FINANCIAL_INTEGRATION_INTERACTIVE_TASKS
)
from .tasks.cross_platform.customer_service import (
    CUSTOMER_SERVICE_TASKS,
    CUSTOMER_SERVICE_INTERACTIVE_TASKS
)

# Single-Platform Task Collections
SINGLE_PLATFORM_TASKS = {
    "salesforce": SALESFORCE_TASKS,
    "servicenow": SERVICENOW_TASKS,
    # Add more platforms as they are implemented
    # "netsuite": NETSUITE_TASKS,
    # "quickbooks": QUICKBOOKS_TASKS,
}

SINGLE_PLATFORM_INTERACTIVE_TASKS = {
    "salesforce": SALESFORCE_INTERACTIVE_TASKS,
    "servicenow": SERVICENOW_INTERACTIVE_TASKS,
    # Add more platforms as they are implemented
    # "netsuite": NETSUITE_INTERACTIVE_TASKS,
    # "quickbooks": QUICKBOOKS_INTERACTIVE_TASKS,
}

# Cross-Platform Task Collections
CROSS_PLATFORM_TASKS = {
    "financial_integration": FINANCIAL_INTEGRATION_TASKS,
    "customer_service": CUSTOMER_SERVICE_TASKS,
    # Add more cross-platform categories as they are implemented
    # "sales_support": SALES_SUPPORT_TASKS,
    # "data_sync": DATA_SYNC_TASKS,
}

CROSS_PLATFORM_INTERACTIVE_TASKS = {
    "financial_integration": FINANCIAL_INTEGRATION_INTERACTIVE_TASKS,
    "customer_service": CUSTOMER_SERVICE_INTERACTIVE_TASKS,
    # Add more cross-platform categories as they are implemented
    # "sales_support": SALES_SUPPORT_INTERACTIVE_TASKS,
    # "data_sync": DATA_SYNC_INTERACTIVE_TASKS,
}

# Combined Task Collections for Easy Access
ALL_SINGLE_PLATFORM_TASKS = []
for platform_tasks in SINGLE_PLATFORM_TASKS.values():
    ALL_SINGLE_PLATFORM_TASKS.extend(platform_tasks)

ALL_SINGLE_PLATFORM_INTERACTIVE_TASKS = []
for platform_tasks in SINGLE_PLATFORM_INTERACTIVE_TASKS.values():
    ALL_SINGLE_PLATFORM_INTERACTIVE_TASKS.extend(platform_tasks)

ALL_CROSS_PLATFORM_TASKS = []
for category_tasks in CROSS_PLATFORM_TASKS.values():
    ALL_CROSS_PLATFORM_TASKS.extend(category_tasks)

ALL_CROSS_PLATFORM_INTERACTIVE_TASKS = []
for category_tasks in CROSS_PLATFORM_INTERACTIVE_TASKS.values():
    ALL_CROSS_PLATFORM_INTERACTIVE_TASKS.extend(category_tasks)

# All Tasks Combined
ALL_TASKS = (
    ALL_SINGLE_PLATFORM_TASKS + 
    ALL_SINGLE_PLATFORM_INTERACTIVE_TASKS + 
    ALL_CROSS_PLATFORM_TASKS + 
    ALL_CROSS_PLATFORM_INTERACTIVE_TASKS
)

# Task Categories for Filtering
TASK_CATEGORIES = {
    "single_platform": {
        "salesforce": ["lead_management", "opportunity_tracking", "case_management", "account_analysis", "sales_performance"],
        "servicenow": ["incident_management", "change_request_analysis", "user_management", "service_catalog", "problem_management"],
        # Add more platforms as they are implemented
    },
    "cross_platform": {
        "financial_integration": ["invoice_to_opportunity", "payment_tracking", "customer_sync", "expense_reconciliation", "financial_reporting"],
        "customer_service": ["incident_to_case", "customer_history_sync", "escalation_workflow", "service_request_fulfillment", "customer_satisfaction_tracking"],
        # Add more categories as they are implemented
    }
}

# External Facing Tasks (for privacy-aware evaluation)
EXTERNAL_FACING_TASKS = [
    "lead_qualification",
    "case_escalation", 
    "opportunity_negotiation",
    "incident_triage",
    "change_approval",
    "service_request",
    "invoice_dispute_resolution",
    "budget_variance_analysis",
    "complex_issue_resolution",
    "customer_retention_analysis"
]

# Platform Schemas (placeholder - will be implemented in schema files)
PLATFORM_SCHEMAS = {
    "salesforce": [],  # Will be loaded from salesforce_schema.py
    "servicenow": [],  # Will be loaded from servicenow_schema.py
    "netsuite": [],    # Will be loaded from netsuite_schema.py
    "quickbooks": [],  # Will be loaded from quickbooks_schema.py
}

def get_tasks_by_platform(platform: str, interactive: bool = False) -> list:
    """Get tasks for a specific platform."""
    if interactive:
        return SINGLE_PLATFORM_INTERACTIVE_TASKS.get(platform, [])
    else:
        return SINGLE_PLATFORM_TASKS.get(platform, [])

def get_tasks_by_category(category: str, interactive: bool = False) -> list:
    """Get tasks for a specific cross-platform category."""
    if interactive:
        return CROSS_PLATFORM_INTERACTIVE_TASKS.get(category, [])
    else:
        return CROSS_PLATFORM_TASKS.get(category, [])

def get_all_tasks(platform: str = None, category: str = None, interactive: bool = False) -> list:
    """Get tasks based on filters."""
    if platform:
        return get_tasks_by_platform(platform, interactive)
    elif category:
        return get_tasks_by_category(category, interactive)
    else:
        if interactive:
            return ALL_SINGLE_PLATFORM_INTERACTIVE_TASKS + ALL_CROSS_PLATFORM_INTERACTIVE_TASKS
        else:
            return ALL_SINGLE_PLATFORM_TASKS + ALL_CROSS_PLATFORM_TASKS

def get_task_by_id(task_id: int) -> dict:
    """Get a specific task by its ID."""
    for task in ALL_TASKS:
        if task.get("idx") == task_id:
            return task
    return None

def get_platforms_for_task(task: dict) -> list:
    """Get the platforms involved in a task."""
    if "platforms" in task:
        return task["platforms"]
    else:
        # Single-platform task - determine platform from task type
        if "salesforce" in task.get("task", ""):
            return ["salesforce"]
        elif "servicenow" in task.get("task", ""):
            return ["servicenow"]
        # Add more platform detection logic as needed
        return ["unknown"]
