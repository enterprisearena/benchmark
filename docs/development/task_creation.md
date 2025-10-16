# Task Creation

This guide explains how to create and define tasks for EnterpriseArena, including both single-platform and cross-platform workflows.

## Task Structure

### Single-Platform Tasks

Single-platform tasks follow the CRMArena format with natural language queries:

```python
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
}
```

### Cross-Platform Tasks

Cross-platform tasks include additional fields for multi-system workflows:

```python
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
}
```

## Task Fields

### Required Fields

- **`idx`**: Unique task identifier (integer)
- **`task`**: Task name/category (string)
- **`query`**: Natural language description of what the agent should do
- **`answer`**: Expected answer(s) (list of strings)
- **`reward_metric`**: How to evaluate the answer ("exact_match", "fuzzy_match", "privacy_rejection")

### Optional Fields

- **`metadata`**: Additional context and instructions
  - **`required`**: Essential information the agent needs
  - **`optional`**: Helpful hints or additional context
- **`platforms`**: List of platforms involved (for cross-platform tasks)
- **`steps`**: Detailed workflow steps (for cross-platform tasks)
- **`persona`**: User persona for interactive tasks
- **`timeout_seconds`**: Maximum execution time
- **`retry_attempts`**: Number of retry attempts

## Creating Single-Platform Tasks

### 1. Choose a Platform

Create tasks in the appropriate platform file:
- `enterprise_sandbox/data/tasks/single_platform/salesforce_tasks.py`
- `enterprise_sandbox/data/tasks/single_platform/servicenow_tasks.py`
- `enterprise_sandbox/data/tasks/single_platform/netsuite_tasks.py`
- `enterprise_sandbox/data/tasks/single_platform/quickbooks_tasks.py`

### 2. Define the Task

```python
{
    "idx": 11,  # Next available ID
    "task": "account_analysis",
    "query": "Find the account with the highest number of contacts and return the account name and contact count.",
    "answer": ["Acme Corporation, 15"],
    "reward_metric": "exact_match",
    "metadata": {
        "required": "Query the Account object and count related Contact records for each account.",
        "optional": "Use a subquery or aggregate function to count contacts per account."
    }
}
```

### 3. Add to Task List

```python
SALESFORCE_TASKS.append({
    "idx": 11,
    "task": "account_analysis",
    # ... rest of task definition
})
```

## Creating Cross-Platform Tasks

### 1. Choose a Category

Create tasks in the appropriate category file:
- `enterprise_sandbox/data/tasks/cross_platform/financial_integration.py`
- `enterprise_sandbox/data/tasks/cross_platform/customer_service.py`
- `enterprise_sandbox/data/tasks/cross_platform/sales_support.py`
- `enterprise_sandbox/data/tasks/cross_platform/data_sync.py`

### 2. Define the Workflow

```python
{
    "idx": 6,
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
}
```

## Interactive Tasks

Interactive tasks support multi-turn conversations:

```python
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
}
```

## Best Practices

### Query Design
- Use clear, natural language
- Be specific about expected outputs
- Include relevant context
- Avoid ambiguous instructions

### Answer Format
- Use consistent formats across similar tasks
- Include multiple valid answers when appropriate
- Be specific about expected data types
- Consider edge cases (empty results, errors)

### Metadata
- Provide essential information in `required`
- Add helpful hints in `optional`
- Include platform-specific guidance
- Mention any special considerations

### Cross-Platform Steps
- Break down complex workflows into logical steps
- Include clear descriptions for each step
- Specify the correct platform for each action
- Consider error handling and recovery

## Testing Tasks

### Validate Task Structure
```python
def validate_task(task):
    required_fields = ['idx', 'task', 'query', 'answer', 'reward_metric']
    for field in required_fields:
        if field not in task:
            raise ValueError(f"Missing required field: {field}")
    
    if 'platforms' in task:
        # Validate cross-platform task
        if 'steps' not in task:
            raise ValueError("Cross-platform tasks must include steps")
    
    return True
```

### Test Task Execution
```bash
# Test single task
python scripts/run_enterprise_arena.py \
    --task_type single_platform \
    --platform salesforce \
    --task_name lead_management

# Test cross-platform task
python scripts/run_enterprise_arena.py \
    --task_type cross_platform \
    --category financial_integration \
    --task_name invoice_to_opportunity
```

## Adding New Task Categories

### 1. Create Category File
```python
# enterprise_sandbox/data/tasks/cross_platform/new_category.py

NEW_CATEGORY_TASKS = [
    # Your tasks here
]

NEW_CATEGORY_INTERACTIVE_TASKS = [
    # Your interactive tasks here
]
```

### 2. Update Assets
```python
# enterprise_sandbox/data/assets.py

from .tasks.cross_platform.new_category import (
    NEW_CATEGORY_TASKS,
    NEW_CATEGORY_INTERACTIVE_TASKS
)

CROSS_PLATFORM_TASKS = {
    "financial_integration": FINANCIAL_INTEGRATION_TASKS,
    "customer_service": CUSTOMER_SERVICE_TASKS,
    "new_category": NEW_CATEGORY_TASKS,  # Add here
}
```

### 3. Update Documentation
- Add category to task creation guide
- Update examples and best practices
- Include in API reference