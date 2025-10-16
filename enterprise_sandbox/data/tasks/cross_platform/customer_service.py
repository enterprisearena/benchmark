"""
Cross-Platform Customer Service Tasks for EnterpriseArena

These tasks involve workflows spanning multiple enterprise platforms,
specifically focusing on customer service integration between systems.
"""

# Cross-Platform Customer Service Tasks
CUSTOMER_SERVICE_TASKS = [
    {
        "idx": 1,
        "task": "incident_to_case",
        "query": "A customer has reported a critical issue through ServiceNow (Incident INC0010001). I need to create a corresponding case in Salesforce and link them together for better tracking.",
        "answer": ["Case created with ID: 500XX000004DHPY"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Extract incident data from ServiceNow, create corresponding case in Salesforce, and establish linkage between the two systems.",
            "optional": "Consider mapping ServiceNow priority levels to Salesforce case priorities."
        },
        "platforms": ["servicenow", "salesforce"],
        "steps": [
            {
                "step_id": "fetch_incident",
                "platform": "servicenow",
                "action": "query",
                "description": "Retrieve incident INC0010001 from ServiceNow"
            },
            {
                "step_id": "transform_data",
                "platform": "transform",
                "action": "transform",
                "description": "Transform ServiceNow incident data to Salesforce case format"
            },
            {
                "step_id": "create_case",
                "platform": "salesforce",
                "action": "create",
                "description": "Create new case in Salesforce with transformed data"
            },
            {
                "step_id": "link_records",
                "platform": "salesforce",
                "action": "update",
                "description": "Update case with ServiceNow incident reference"
            }
        ]
    },
    {
        "idx": 2,
        "task": "customer_history_sync",
        "query": "I need to pull the complete customer interaction history from ServiceNow for account 'Global Enterprises' and update their Salesforce account record with this information.",
        "answer": ["Account updated with 15 interaction records"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query customer interactions from ServiceNow, find corresponding account in Salesforce, and update with interaction history.",
            "optional": "Consider data format differences and create a summary of interaction types."
        },
        "platforms": ["servicenow", "salesforce"],
        "steps": [
            {
                "step_id": "get_interactions",
                "platform": "servicenow",
                "action": "query",
                "description": "Retrieve all interactions for Global Enterprises from ServiceNow"
            },
            {
                "step_id": "find_account",
                "platform": "salesforce",
                "action": "query",
                "description": "Find Global Enterprises account in Salesforce"
            },
            {
                "step_id": "process_history",
                "platform": "transform",
                "action": "transform",
                "description": "Process and format interaction history data"
            },
            {
                "step_id": "update_account",
                "platform": "salesforce",
                "action": "update",
                "description": "Update Salesforce account with interaction history"
            }
        ]
    },
    {
        "idx": 3,
        "task": "escalation_workflow",
        "query": "A ServiceNow incident (INC0010002) has been escalated to the sales team. I need to create a lead in Salesforce and link it to the incident for follow-up.",
        "answer": ["Lead created with ID: 00QXX000004DHPY"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Extract escalated incident data from ServiceNow, create lead in Salesforce, and establish linkage for sales follow-up.",
            "optional": "Consider the escalation reason and customer value when creating the lead."
        },
        "platforms": ["servicenow", "salesforce"],
        "steps": [
            {
                "step_id": "get_escalated_incident",
                "platform": "servicenow",
                "action": "query",
                "description": "Retrieve escalated incident INC0010002 from ServiceNow"
            },
            {
                "step_id": "extract_customer_data",
                "platform": "transform",
                "action": "transform",
                "description": "Extract customer information from incident data"
            },
            {
                "step_id": "create_lead",
                "platform": "salesforce",
                "action": "create",
                "description": "Create new lead in Salesforce with customer data"
            },
            {
                "step_id": "link_incident",
                "platform": "salesforce",
                "action": "update",
                "description": "Link lead to ServiceNow incident for tracking"
            }
        ]
    },
    {
        "idx": 4,
        "task": "service_request_fulfillment",
        "query": "A customer has requested a new service through ServiceNow (Request REQ0010001). I need to create a corresponding opportunity in Salesforce to track the potential sale.",
        "answer": ["Opportunity created with ID: 006XX000004DHPY"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Extract service request data from ServiceNow, create opportunity in Salesforce, and establish linkage for sales tracking.",
            "optional": "Consider the service type and customer value when setting opportunity amount and probability."
        },
        "platforms": ["servicenow", "salesforce"],
        "steps": [
            {
                "step_id": "get_service_request",
                "platform": "servicenow",
                "action": "query",
                "description": "Retrieve service request REQ0010001 from ServiceNow"
            },
            {
                "step_id": "assess_opportunity",
                "platform": "transform",
                "action": "transform",
                "description": "Assess the service request for sales opportunity potential"
            },
            {
                "step_id": "create_opportunity",
                "platform": "salesforce",
                "action": "create",
                "description": "Create opportunity in Salesforce if viable"
            },
            {
                "step_id": "link_request",
                "platform": "salesforce",
                "action": "update",
                "description": "Link opportunity to ServiceNow request"
            }
        ]
    },
    {
        "idx": 5,
        "task": "customer_satisfaction_tracking",
        "query": "I need to analyze customer satisfaction by comparing resolved ServiceNow incidents with customer feedback in Salesforce. Find all incidents resolved in the last month and check for corresponding customer feedback.",
        "answer": ["Satisfaction analysis completed - 85% satisfaction rate"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query resolved incidents from ServiceNow, find corresponding customer feedback in Salesforce, and analyze satisfaction metrics.",
            "optional": "Consider response time, resolution quality, and customer value in the analysis."
        },
        "platforms": ["servicenow", "salesforce"],
        "steps": [
            {
                "step_id": "get_resolved_incidents",
                "platform": "servicenow",
                "action": "query",
                "description": "Retrieve incidents resolved in the last month from ServiceNow"
            },
            {
                "step_id": "get_customer_feedback",
                "platform": "salesforce",
                "action": "query",
                "description": "Retrieve customer feedback records from Salesforce"
            },
            {
                "step_id": "match_data",
                "platform": "transform",
                "action": "transform",
                "description": "Match incidents with customer feedback"
            },
            {
                "step_id": "analyze_satisfaction",
                "platform": "transform",
                "action": "transform",
                "description": "Analyze customer satisfaction metrics"
            }
        ]
    }
]

# Cross-Platform Customer Service Interactive Tasks
CUSTOMER_SERVICE_INTERACTIVE_TASKS = [
    {
        "idx": 1,
        "task": "complex_issue_resolution",
        "query": "A customer is experiencing a complex technical issue that spans multiple systems. The issue started as a ServiceNow incident (INC0010003) but now involves their Salesforce integration. I need to coordinate resolution across both systems.",
        "persona": "You are a senior support engineer coordinating resolution of a complex, multi-system issue. You need to gather information from both systems and coordinate with different teams.",
        "answer": ["Issue resolved with coordinated fix across both systems"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Investigate the complex issue across both ServiceNow and Salesforce, coordinate with relevant teams, and provide a comprehensive resolution.",
            "optional": "Consider the impact on the customer's business operations and provide regular updates throughout the resolution process."
        },
        "platforms": ["servicenow", "salesforce"]
    },
    {
        "idx": 2,
        "task": "customer_retention_analysis",
        "query": "A high-value customer is showing signs of dissatisfaction based on their recent ServiceNow incidents and Salesforce case history. I need to analyze their situation and recommend retention strategies.",
        "persona": "You are a customer success manager analyzing a customer at risk of churning. You need to review their complete interaction history and develop a retention strategy.",
        "answer": ["Retention strategy developed with 3 key action items"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Analyze the customer's complete interaction history across both systems, identify pain points, and develop a comprehensive retention strategy.",
            "optional": "Consider the customer's contract value, usage patterns, and competitive landscape when developing the strategy."
        },
        "platforms": ["servicenow", "salesforce"]
    }
]
