"""
ServiceNow Single-Platform Tasks for EnterpriseArena

These tasks are defined in natural language similar to CRMArena benchmark,
with query, answer, and metadata fields.
"""

# ServiceNow Single-Platform Tasks
SERVICENOW_TASKS = [
    {
        "idx": 1,
        "task": "incident_management",
        "query": "Find all high priority incidents that are still open and return the incident numbers.",
        "answer": ["INC0010001", "INC0010002"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the incident table for records where priority is '1 - Critical' and state is not 'Closed'.",
            "optional": "Return the number field for each matching incident."
        }
    },
    {
        "idx": 2,
        "task": "change_request_analysis",
        "query": "What is the average time to implement change requests in the 'Infrastructure' category?",
        "answer": ["5.2 days"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query change requests in the 'Infrastructure' category and calculate the average implementation time.",
            "optional": "Use the opened_at and closed_at fields to calculate implementation duration."
        }
    },
    {
        "idx": 3,
        "task": "user_management",
        "query": "How many active users are in the 'IT Support' group?",
        "answer": ["23"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the sys_user table for users in the 'IT Support' group with active status.",
            "optional": "Filter by active=true and group membership."
        }
    },
    {
        "idx": 4,
        "task": "service_catalog",
        "query": "What are the top 3 most requested catalog items this month?",
        "answer": ["Laptop Request", "Software Installation", "VPN Access"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the sc_request table for requests created this month and count by catalog item.",
            "optional": "Group by catalog item and order by count descending."
        }
    },
    {
        "idx": 5,
        "task": "problem_management",
        "query": "Find all problems with root cause 'Hardware Failure' and return their numbers.",
        "answer": ["PRB0010001", "PRB0010002"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the problem table for records where root_cause equals 'Hardware Failure'.",
            "optional": "Return the number field for each matching problem."
        }
    },
    {
        "idx": 6,
        "task": "knowledge_management",
        "query": "How many knowledge articles are published in the 'Troubleshooting' category?",
        "answer": ["47"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the kb_knowledge table for articles in the 'Troubleshooting' category with published status.",
            "optional": "Filter by category and work_flow_state='published'."
        }
    },
    {
        "idx": 7,
        "task": "asset_management",
        "query": "What is the total value of all laptops in the asset database?",
        "answer": ["$125,000"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the alm_asset table for assets with model_name containing 'laptop' and sum the cost field.",
            "optional": "Filter by asset class or model name to identify laptops."
        }
    },
    {
        "idx": 8,
        "task": "sla_management",
        "query": "How many incidents breached their SLA in the last week?",
        "answer": ["8"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query incidents created in the last week and check for SLA breach status.",
            "optional": "Use the sla_due field and current time to determine breaches."
        }
    },
    {
        "idx": 9,
        "task": "vendor_management",
        "query": "Which vendor has the most open incidents assigned to them?",
        "answer": ["TechSupport Inc, 12"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query incidents with assigned vendor and count by vendor for open incidents.",
            "optional": "Group by vendor and filter by state not equal to 'Closed'."
        }
    },
    {
        "idx": 10,
        "task": "configuration_management",
        "query": "Find all configuration items with 'End of Life' status and return their names.",
        "answer": ["Server-Web-01", "Router-Core-02"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the cmdb_ci table for configuration items with lifecycle_stage='end_of_life'.",
            "optional": "Return the name field for each matching configuration item."
        }
    }
]

# ServiceNow Interactive Tasks (Multi-turn conversations)
SERVICENOW_INTERACTIVE_TASKS = [
    {
        "idx": 1,
        "task": "incident_triage",
        "query": "I have a new incident reported by a user. They're saying their computer is running very slowly and they can't access their email. The user is from the Finance department.",
        "persona": "You are an IT support technician helping to triage a new incident. You need to gather more information to properly categorize and assign the incident.",
        "answer": ["Assigned to Desktop Support Team"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Help triage the incident by asking relevant questions about symptoms, impact, and user details.",
            "optional": "Consider the user's department and the nature of the issue when determining priority and assignment."
        }
    },
    {
        "idx": 2,
        "task": "change_approval",
        "query": "I need to request a change to update the production database server. This is a critical system that affects all users. The change involves applying a security patch.",
        "persona": "You are a change manager reviewing a change request. You need to understand the impact, risk, and approval requirements.",
        "answer": ["Approved with CAB review"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Help process the change request by gathering information about impact, risk, and approval requirements.",
            "optional": "Consider the criticality of the system and the nature of the change when determining approval process."
        }
    },
    {
        "idx": 3,
        "task": "service_request",
        "query": "A new employee is starting next week and needs a laptop, software licenses, and access to various systems. They're joining the Marketing team.",
        "persona": "You are a service desk agent helping to fulfill a new employee onboarding request. You need to understand all the requirements and coordinate with different teams.",
        "answer": ["Created service request with multiple catalog items"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Help create a comprehensive service request by identifying all required items and access needs.",
            "optional": "Consider the employee's role and department when determining software and access requirements."
        }
    }
]
