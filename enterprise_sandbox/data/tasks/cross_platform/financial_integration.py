"""
Cross-Platform Financial Integration Tasks for EnterpriseArena

These tasks involve workflows spanning multiple enterprise platforms,
specifically focusing on financial data integration between systems.
"""

# Cross-Platform Financial Integration Tasks
FINANCIAL_INTEGRATION_TASKS = [
    {
        "idx": 1,
        "task": "invoice_to_opportunity",
        "query": "I have a new invoice from QuickBooks for customer 'Acme Corporation' with invoice number INV-2024-001. I need to create a corresponding opportunity in Salesforce and link them together.",
        "answer": ["Opportunity created with ID: 006XX000004DHPY"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Extract invoice data from QuickBooks, transform it for Salesforce format, create opportunity, and establish linkage.",
            "optional": "Consider mapping invoice line items to opportunity products if applicable."
        },
        "platforms": ["quickbooks", "salesforce"],
        "steps": [
            {
                "step_id": "fetch_invoice",
                "platform": "quickbooks",
                "action": "query",
                "description": "Retrieve invoice INV-2024-001 for Acme Corporation from QuickBooks"
            },
            {
                "step_id": "transform_data",
                "platform": "transform",
                "action": "transform",
                "description": "Transform QuickBooks invoice data to Salesforce opportunity format"
            },
            {
                "step_id": "create_opportunity",
                "platform": "salesforce",
                "action": "create",
                "description": "Create new opportunity in Salesforce with transformed data"
            },
            {
                "step_id": "link_records",
                "platform": "salesforce",
                "action": "update",
                "description": "Update opportunity with QuickBooks invoice reference"
            }
        ]
    },
    {
        "idx": 2,
        "task": "payment_tracking",
        "query": "Check the payment status of invoice INV-2024-002 in QuickBooks and update the corresponding opportunity stage in Salesforce based on the payment status.",
        "answer": ["Opportunity stage updated to 'Closed Won'"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Query payment status in QuickBooks, find corresponding opportunity in Salesforce, and update stage accordingly.",
            "optional": "Consider partial payments and their impact on opportunity stage."
        },
        "platforms": ["quickbooks", "salesforce"],
        "steps": [
            {
                "step_id": "check_payment",
                "platform": "quickbooks",
                "action": "query",
                "description": "Check payment status of invoice INV-2024-002 in QuickBooks"
            },
            {
                "step_id": "find_opportunity",
                "platform": "salesforce",
                "action": "query",
                "description": "Find the opportunity linked to invoice INV-2024-002"
            },
            {
                "step_id": "update_stage",
                "platform": "salesforce",
                "action": "update",
                "description": "Update opportunity stage based on payment status"
            }
        ]
    },
    {
        "idx": 3,
        "task": "customer_sync",
        "query": "Synchronize customer data between QuickBooks and Salesforce. Find customers in QuickBooks that don't exist in Salesforce and create them as accounts.",
        "answer": ["3 new accounts created in Salesforce"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Compare customer lists between systems, identify missing customers, and create accounts in Salesforce.",
            "optional": "Handle data mapping differences between the two systems."
        },
        "platforms": ["quickbooks", "salesforce"],
        "steps": [
            {
                "step_id": "get_qb_customers",
                "platform": "quickbooks",
                "action": "query",
                "description": "Retrieve all customers from QuickBooks"
            },
            {
                "step_id": "get_sf_accounts",
                "platform": "salesforce",
                "action": "query",
                "description": "Retrieve all accounts from Salesforce"
            },
            {
                "step_id": "compare_data",
                "platform": "transform",
                "action": "transform",
                "description": "Compare customer lists and identify missing customers"
            },
            {
                "step_id": "create_accounts",
                "platform": "salesforce",
                "action": "create",
                "description": "Create missing customers as accounts in Salesforce"
            }
        ]
    },
    {
        "idx": 4,
        "task": "expense_reconciliation",
        "query": "Reconcile expenses between NetSuite and QuickBooks for the current month. Find any discrepancies in expense amounts and create adjustment entries.",
        "answer": ["2 discrepancies found and reconciled"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Compare expense data between NetSuite and QuickBooks, identify discrepancies, and create reconciliation entries.",
            "optional": "Consider timing differences and currency conversions if applicable."
        },
        "platforms": ["netsuite", "quickbooks"],
        "steps": [
            {
                "step_id": "get_netsuite_expenses",
                "platform": "netsuite",
                "action": "query",
                "description": "Retrieve expenses from NetSuite for current month"
            },
            {
                "step_id": "get_qb_expenses",
                "platform": "quickbooks",
                "action": "query",
                "description": "Retrieve expenses from QuickBooks for current month"
            },
            {
                "step_id": "compare_expenses",
                "platform": "transform",
                "action": "transform",
                "description": "Compare expense data and identify discrepancies"
            },
            {
                "step_id": "create_adjustments",
                "platform": "netsuite",
                "action": "create",
                "description": "Create adjustment entries for discrepancies"
            }
        ]
    },
    {
        "idx": 5,
        "task": "financial_reporting",
        "query": "Generate a consolidated financial report by combining revenue data from Salesforce opportunities with actual invoice data from QuickBooks for Q1 2024.",
        "answer": ["Consolidated report generated with $2.5M revenue"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Extract revenue data from both systems, consolidate the information, and generate a comprehensive report.",
            "optional": "Include variance analysis between forecasted and actual revenue."
        },
        "platforms": ["salesforce", "quickbooks"],
        "steps": [
            {
                "step_id": "get_sf_revenue",
                "platform": "salesforce",
                "action": "query",
                "description": "Retrieve closed won opportunities for Q1 2024 from Salesforce"
            },
            {
                "step_id": "get_qb_invoices",
                "platform": "quickbooks",
                "action": "query",
                "description": "Retrieve paid invoices for Q1 2024 from QuickBooks"
            },
            {
                "step_id": "consolidate_data",
                "platform": "transform",
                "action": "transform",
                "description": "Consolidate and analyze revenue data from both systems"
            },
            {
                "step_id": "generate_report",
                "platform": "transform",
                "action": "create",
                "description": "Generate consolidated financial report"
            }
        ]
    }
]

# Cross-Platform Financial Integration Interactive Tasks
FINANCIAL_INTEGRATION_INTERACTIVE_TASKS = [
    {
        "idx": 1,
        "task": "invoice_dispute_resolution",
        "query": "A customer is disputing an invoice from QuickBooks. The invoice number is INV-2024-003 and they claim the amount is incorrect. I need to investigate this across both QuickBooks and Salesforce to understand the issue and resolve it.",
        "persona": "You are a customer service representative handling an invoice dispute. You need to investigate the issue across multiple systems and provide a resolution.",
        "answer": ["Dispute resolved with $500 credit applied"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Investigate the invoice dispute by examining data in both QuickBooks and Salesforce, identify the issue, and provide a resolution.",
            "optional": "Consider the customer's history and the impact on their account when determining the resolution."
        },
        "platforms": ["quickbooks", "salesforce"]
    },
    {
        "idx": 2,
        "task": "budget_variance_analysis",
        "query": "I need to analyze the budget variance for our sales team. The budget was set in NetSuite, but actual expenses are tracked in QuickBooks. Can you help me understand the differences?",
        "persona": "You are a financial analyst helping to analyze budget variances. You need to compare budgeted amounts with actual expenses across different systems.",
        "answer": ["Budget variance analysis completed - 15% over budget"],
        "reward_metric": "exact_match",
        "metadata": {
            "required": "Compare budgeted amounts from NetSuite with actual expenses from QuickBooks and analyze the variances.",
            "optional": "Provide insights on the largest variance categories and recommendations for budget management."
        },
        "platforms": ["netsuite", "quickbooks"]
    }
]
