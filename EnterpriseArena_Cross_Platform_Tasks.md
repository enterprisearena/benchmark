# EnterpriseArena Cross-Platform Task Framework

## Overview
The cross-platform task framework enables evaluation of LLM agents performing workflows that span multiple enterprise software platforms. This extends beyond single-platform tasks to complex business processes that require coordination across different systems.

## Task Categories

### 1. Financial Integration Tasks
**QuickBooks ↔ Salesforce**
- **Invoice to Opportunity**: Extract invoice data from QuickBooks, create opportunity in Salesforce
- **Payment Tracking**: Update Salesforce opportunity stage based on QuickBooks payment status
- **Customer Sync**: Sync customer data between QuickBooks and Salesforce

**NetSuite ↔ QuickBooks**
- **Financial Reporting**: Generate consolidated reports from both systems
- **Expense Reconciliation**: Match expenses between NetSuite and QuickBooks
- **Inventory Valuation**: Cross-reference inventory values between systems

### 2. Customer Service Integration
**ServiceNow ↔ Salesforce**
- **Case to Lead**: Convert ServiceNow incident to Salesforce lead
- **Customer History**: Pull customer interaction history from ServiceNow into Salesforce
- **Escalation Workflow**: Escalate ServiceNow cases to Salesforce for sales follow-up

### 3. Sales and Support Coordination
**Salesforce ↔ ServiceNow ↔ NetSuite**
- **Quote to Order**: Convert Salesforce quote to NetSuite sales order
- **Support to Upsell**: Identify upsell opportunities from ServiceNow support cases
- **Customer Lifecycle**: Track customer journey across all three platforms

### 4. Data Synchronization Tasks
**Multi-Platform Sync**
- **Customer Master Data**: Maintain consistent customer records across platforms
- **Product Catalog Sync**: Synchronize product information across systems
- **User Management**: Sync user accounts and permissions across platforms

## Task Definition Structure

### Cross-Platform Task Schema
```python
@dataclass
class CrossPlatformTask:
    task_id: str
    name: str
    description: str
    category: str  # financial_integration, customer_service, etc.
    platforms: List[str]  # ["salesforce", "quickbooks"]
    complexity: str  # "simple", "moderate", "complex"
    steps: List[TaskStep]
    dependencies: Dict[str, List[str]]  # step_id -> [dependent_step_ids]
    expected_output: Any
    evaluation_metric: str
    timeout_seconds: int = 300
    retry_attempts: int = 3
```

### Task Step Schema
```python
@dataclass
class TaskStep:
    step_id: str
    name: str
    platform: str
    action_type: str  # "query", "create", "update", "delete", "transform"
    parameters: Dict[str, Any]
    input_mapping: Dict[str, str]  # Maps previous step outputs to this step's inputs
    output_mapping: Dict[str, str]  # Maps this step's outputs for next steps
    validation_rules: List[ValidationRule]
    error_handling: ErrorHandlingStrategy
    timeout_seconds: int = 60
```

### Example: Invoice to Opportunity Task
```python
invoice_to_opportunity_task = CrossPlatformTask(
    task_id="invoice_to_opportunity_001",
    name="Convert QuickBooks Invoice to Salesforce Opportunity",
    description="Extract invoice data from QuickBooks and create corresponding opportunity in Salesforce",
    category="financial_integration",
    platforms=["quickbooks", "salesforce"],
    complexity="moderate",
    steps=[
        TaskStep(
            step_id="fetch_invoice",
            name="Fetch Invoice from QuickBooks",
            platform="quickbooks",
            action_type="query",
            parameters={
                "query": "SELECT * FROM Invoice WHERE Id = {invoice_id}",
                "include_line_items": True
            },
            input_mapping={"invoice_id": "task_input.invoice_id"},
            output_mapping={"invoice_data": "invoice", "customer_data": "customer"}
        ),
        TaskStep(
            step_id="transform_data",
            name="Transform Invoice Data",
            platform="transform",  # Special platform for data transformation
            action_type="transform",
            parameters={
                "mapping_rules": {
                    "opportunity_name": "{invoice_data.CustomerRef.name} - {invoice_data.DocNumber}",
                    "amount": "{invoice_data.TotalAmt}",
                    "close_date": "{invoice_data.DueDate}",
                    "stage": "Prospecting"
                }
            },
            input_mapping={"invoice_data": "fetch_invoice.invoice_data"},
            output_mapping={"opportunity_data": "transformed_opportunity"}
        ),
        TaskStep(
            step_id="create_opportunity",
            name="Create Opportunity in Salesforce",
            platform="salesforce",
            action_type="create",
            parameters={
                "object_type": "Opportunity",
                "data": "{transformed_opportunity}"
            },
            input_mapping={"transformed_opportunity": "transform_data.opportunity_data"},
            output_mapping={"opportunity_id": "created_opportunity_id"}
        )
    ],
    dependencies={
        "transform_data": ["fetch_invoice"],
        "create_opportunity": ["transform_data"]
    },
    expected_output={"opportunity_id": "string", "success": "boolean"},
    evaluation_metric="exact_match"
)
```

## Cross-Platform Execution Engine

### Orchestration Engine
```python
class CrossPlatformOrchestrationEngine:
    def __init__(self, platform_connections: Dict[str, BasePlatform]):
        self.platform_connections = platform_connections
        self.execution_context = {}
        self.step_results = {}
    
    async def execute_task(self, task: CrossPlatformTask) -> Dict[str, Any]:
        """Execute a cross-platform task with proper dependency management"""
        try:
            # Validate task dependencies
            self._validate_dependencies(task)
            
            # Execute steps in dependency order
            execution_order = self._topological_sort(task.steps, task.dependencies)
            
            for step in execution_order:
                result = await self._execute_step(step, task)
                self.step_results[step.step_id] = result
                
                # Update execution context for next steps
                self._update_context(step, result)
            
            return self._generate_final_result(task)
            
        except Exception as e:
            return self._handle_execution_error(e, task)
    
    async def _execute_step(self, step: TaskStep, task: CrossPlatformTask) -> Dict[str, Any]:
        """Execute a single step with proper error handling and retries"""
        for attempt in range(step.retry_attempts):
            try:
                # Resolve input parameters
                resolved_params = self._resolve_parameters(step.parameters, step.input_mapping)
                
                # Execute step on target platform
                if step.platform == "transform":
                    result = await self._execute_transform(step, resolved_params)
                else:
                    platform = self.platform_connections[step.platform]
                    result = await platform.execute_action(step.action_type, resolved_params)
                
                # Validate result
                self._validate_step_result(step, result)
                
                return result
                
            except Exception as e:
                if attempt == step.retry_attempts - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Data Flow and Context Management

### Execution Context
```python
@dataclass
class ExecutionContext:
    task_input: Dict[str, Any]
    step_results: Dict[str, Dict[str, Any]]
    platform_states: Dict[str, Dict[str, Any]]
    error_log: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    
    def get_value(self, path: str) -> Any:
        """Get value from context using dot notation (e.g., 'step1.output.field')"""
        parts = path.split('.')
        current = self
        
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise ValueError(f"Path {path} not found in context")
        
        return current
```

### Parameter Resolution
```python
class ParameterResolver:
    def __init__(self, context: ExecutionContext):
        self.context = context
    
    def resolve_parameters(self, parameters: Dict[str, Any], input_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Resolve parameters using context and input mapping"""
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                # Template parameter
                template = value[1:-1]  # Remove braces
                resolved[key] = self._resolve_template(template)
            else:
                resolved[key] = value
        
        return resolved
    
    def _resolve_template(self, template: str) -> Any:
        """Resolve template string using context"""
        # Handle simple variable references
        if '.' in template:
            return self.context.get_value(template)
        else:
            # Handle complex expressions (future enhancement)
            return self._evaluate_expression(template)
```

## Error Handling and Recovery

### Error Handling Strategies
```python
@dataclass
class ErrorHandlingStrategy:
    strategy_type: str  # "retry", "skip", "abort", "fallback"
    max_retries: int = 3
    retry_delay: int = 5
    fallback_action: Optional[str] = None
    error_mapping: Dict[str, str] = None  # Map error types to handling strategies
```

### Error Recovery Mechanisms
1. **Retry with Backoff**: Exponential backoff for transient errors
2. **Step Skipping**: Skip non-critical steps if they fail
3. **Fallback Actions**: Execute alternative actions when primary fails
4. **Partial Success**: Return partial results when some steps succeed
5. **Rollback**: Undo completed steps if later steps fail

## Evaluation Framework

### Cross-Platform Evaluation Metrics
```python
class CrossPlatformEvaluator:
    def __init__(self):
        self.metrics = {
            "task_completion_rate": self._calculate_completion_rate,
            "step_success_rate": self._calculate_step_success_rate,
            "data_accuracy": self._calculate_data_accuracy,
            "execution_efficiency": self._calculate_execution_efficiency,
            "error_recovery_rate": self._calculate_error_recovery_rate
        }
    
    def evaluate_task(self, task: CrossPlatformTask, execution_result: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate cross-platform task execution"""
        evaluation = {}
        
        for metric_name, metric_func in self.metrics.items():
            evaluation[metric_name] = metric_func(task, execution_result)
        
        return evaluation
```

### Evaluation Criteria
1. **Functional Correctness**: Did the task produce the expected output?
2. **Data Integrity**: Is the data correctly transformed and synchronized?
3. **Error Handling**: How well did the agent handle errors and edge cases?
4. **Performance**: How efficiently was the task executed?
5. **Platform Coordination**: How well did the agent coordinate across platforms?

## Task Library Examples

### 1. Simple Cross-Platform Task
```python
# QuickBooks Customer to Salesforce Lead
simple_customer_sync = CrossPlatformTask(
    task_id="customer_sync_001",
    name="Sync Customer from QuickBooks to Salesforce",
    platforms=["quickbooks", "salesforce"],
    steps=[
        TaskStep(
            step_id="fetch_customer",
            platform="quickbooks",
            action_type="query",
            parameters={"query": "SELECT * FROM Customer WHERE Id = {customer_id}"}
        ),
        TaskStep(
            step_id="create_lead",
            platform="salesforce",
            action_type="create",
            parameters={
                "object_type": "Lead",
                "data": {
                    "FirstName": "{fetch_customer.GivenName}",
                    "LastName": "{fetch_customer.FamilyName}",
                    "Email": "{fetch_customer.PrimaryEmailAddr.Address}",
                    "Company": "{fetch_customer.CompanyName}"
                }
            }
        )
    ]
)
```

### 2. Complex Multi-Step Task
```python
# ServiceNow Incident to Salesforce Case to NetSuite Project
complex_incident_workflow = CrossPlatformTask(
    task_id="incident_to_project_001",
    name="Convert ServiceNow Incident to Salesforce Case and NetSuite Project",
    platforms=["servicenow", "salesforce", "netsuite"],
    steps=[
        # Step 1: Fetch incident from ServiceNow
        TaskStep(
            step_id="fetch_incident",
            platform="servicenow",
            action_type="query",
            parameters={"query": "SELECT * FROM incident WHERE sys_id = {incident_id}"}
        ),
        # Step 2: Create case in Salesforce
        TaskStep(
            step_id="create_case",
            platform="salesforce",
            action_type="create",
            parameters={
                "object_type": "Case",
                "data": {
                    "Subject": "{fetch_incident.short_description}",
                    "Description": "{fetch_incident.description}",
                    "Priority": "{fetch_incident.priority}",
                    "Status": "New"
                }
            }
        ),
        # Step 3: Create project in NetSuite
        TaskStep(
            step_id="create_project",
            platform="netsuite",
            action_type="create",
            parameters={
                "record_type": "project",
                "data": {
                    "title": "{fetch_incident.short_description}",
                    "description": "{fetch_incident.description}",
                    "status": "In Progress"
                }
            }
        ),
        # Step 4: Link case and project
        TaskStep(
            step_id="link_records",
            platform="salesforce",
            action_type="update",
            parameters={
                "object_type": "Case",
                "record_id": "{create_case.id}",
                "data": {
                    "External_Project_ID__c": "{create_project.id}"
                }
            }
        )
    ]
)
```

This cross-platform task framework provides a robust foundation for evaluating LLM agents on complex, multi-system workflows that mirror real-world enterprise scenarios.
