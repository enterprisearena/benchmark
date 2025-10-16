"""
Salesforce Single-Platform Tasks for EnterpriseArena

These tasks are defined in natural language similar to CRMArena benchmark,
with query, answer, and metadata fields.
"""

# Salesforce Single-Platform Tasks
SALESFORCE_TASKS = [
    {
        "idx": 1,
        "task": "lead_management",
        "query": "Find all leads created in the last 30 days and return their names and email addresses.",
        "answer": ["John Smith, john.smith@email.com", "Jane Doe, jane.doe@email.com"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "You need to query the Lead object for records created in the last 30 days.",
            "optional": "Consider using the CreatedDate field with appropriate date filtering."
        }
    },
    {
        "idx": 2,
        "task": "opportunity_tracking",
        "query": "What is the total value of all opportunities in the 'Closed Won' stage?",
        "answer": ["$2,500,000"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the Opportunity object and sum the Amount field for records where StageName equals 'Closed Won'.",
            "optional": "You may need to handle null values in the Amount field."
        }
    },
    {
        "idx": 3,
        "task": "case_management",
        "query": "Find all high priority cases that are still open and return the case numbers.",
        "answer": ["00001001", "00001002"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the Case object for records where Priority is 'High' and Status is not 'Closed'.",
            "optional": "Return the CaseNumber field for each matching record."
        }
    },
    {
        "idx": 4,
        "task": "account_analysis",
        "query": "Which account has the highest number of contacts? Return the account name and contact count.",
        "answer": ["Acme Corporation, 15"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the Account object and count related Contact records for each account.",
            "optional": "Use a subquery or aggregate function to count contacts per account."
        }
    },
    {
        "idx": 5,
        "task": "sales_performance",
        "query": "What is the average deal size for opportunities closed in the current quarter?",
        "answer": ["$125,000"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query opportunities closed in the current quarter and calculate the average amount.",
            "optional": "Filter by CloseDate for the current quarter and StageName for closed opportunities."
        }
    },
    {
        "idx": 6,
        "task": "lead_conversion",
        "query": "How many leads were converted to opportunities in the last month?",
        "answer": ["45"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the Lead object for records converted in the last month.",
            "optional": "Use the ConvertedDate field or IsConverted field to identify converted leads."
        }
    },
    {
        "idx": 7,
        "task": "contact_search",
        "query": "Find all contacts with the last name 'Johnson' and return their phone numbers.",
        "answer": ["555-0123", "555-0456"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the Contact object where LastName equals 'Johnson'.",
            "optional": "Return the Phone field for each matching contact."
        }
    },
    {
        "idx": 8,
        "task": "opportunity_pipeline",
        "query": "What is the total pipeline value for opportunities in the 'Proposal' stage?",
        "answer": ["$1,200,000"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the Opportunity object and sum the Amount field for records where StageName equals 'Proposal'.",
            "optional": "Consider using the SUM() function in your query."
        }
    },
    {
        "idx": 9,
        "task": "case_resolution",
        "query": "What is the average time to resolve cases in the 'Technical Support' category?",
        "answer": ["3.5 days"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query cases in the 'Technical Support' category and calculate the average resolution time.",
            "optional": "Use the CreatedDate and ClosedDate fields to calculate resolution time."
        }
    },
    {
        "idx": 10,
        "task": "account_territory",
        "query": "Which territory has the most accounts? Return the territory name and account count.",
        "answer": ["West Coast, 25"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query the Account object and group by territory to count accounts per territory.",
            "optional": "Use the Territory field or related Territory object if available."
        }
    }
]

# Salesforce Interactive Tasks (Multi-turn conversations)
SALESFORCE_INTERACTIVE_TASKS = [
    {
        "idx": 1,
        "task": "lead_qualification",
        "query": "I need help qualifying a new lead. The lead is from a company called TechCorp and the contact person is Sarah Wilson.",
        "persona": "You are a sales representative looking to qualify a new lead. You want to understand if this lead is worth pursuing based on company size, industry, and budget.",
        "answer": ["Qualified - High Priority"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Help the user qualify the lead by asking relevant questions about company size, industry, budget, and timeline.",
            "optional": "Use BANT (Budget, Authority, Need, Timeline) qualification criteria."
        }
    },
    {
        "idx": 2,
        "task": "case_escalation",
        "query": "I have a customer who is very upset about a billing issue. The case number is 00001001 and they're threatening to cancel their contract.",
        "persona": "You are a customer service representative dealing with an escalated case. You need to understand the issue and provide a resolution.",
        "answer": ["Escalated to Billing Team"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Help resolve the customer's billing issue by gathering information and providing appropriate escalation or resolution.",
            "optional": "Consider the customer's contract value and history when determining the best approach."
        }
    },
    {
        "idx": 3,
        "task": "opportunity_negotiation",
        "query": "I'm working on a large opportunity with Global Enterprises. The deal is worth $500,000 but they're asking for a 15% discount. What should I do?",
        "persona": "You are a sales manager helping a sales rep with a large deal negotiation. You need to consider the deal size, discount impact, and closing probability.",
        "answer": ["Approved 10% discount with payment terms"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Help negotiate the deal by considering the discount impact on margins and suggesting alternative approaches.",
            "optional": "Consider the customer's payment history and the competitive landscape."
        }
    }
]
