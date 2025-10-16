# API Reference

This document provides comprehensive API reference for EnterpriseArena components.

## Core Modules

### Data Assets

#### `enterprise_sandbox.data.assets`

```python
from enterprise_sandbox.data.assets import (
    ALL_TASKS,
    ALL_SINGLE_PLATFORM_TASKS,
    ALL_CROSS_PLATFORM_TASKS,
    SINGLE_PLATFORM_TASKS,
    CROSS_PLATFORM_TASKS,
    get_tasks_by_platform,
    get_tasks_by_category,
    get_all_tasks,
    get_task_by_id,
    get_platforms_for_task
)
```

**Functions:**

- `get_tasks_by_platform(platform: str, interactive: bool = False) -> List[Dict]`
  - Get tasks for a specific platform
  - Parameters: platform name, whether to include interactive tasks
  - Returns: List of task dictionaries

- `get_tasks_by_category(category: str, interactive: bool = False) -> List[Dict]`
  - Get tasks for a specific cross-platform category
  - Parameters: category name, whether to include interactive tasks
  - Returns: List of task dictionaries

- `get_all_tasks(platform: str = None, category: str = None, interactive: bool = False) -> List[Dict]`
  - Get tasks based on filters
  - Parameters: optional platform/category filters, interactive flag
  - Returns: Filtered list of tasks

- `get_task_by_id(task_id: int) -> Dict`
  - Get a specific task by its ID
  - Parameters: task ID
  - Returns: Task dictionary or None

- `get_platforms_for_task(task: Dict) -> List[str]`
  - Get the platforms involved in a task
  - Parameters: task dictionary
  - Returns: List of platform names

### Platform Abstraction

#### `enterprise_sandbox.platforms.base.platform`

```python
from enterprise_sandbox.platforms.base.platform import BasePlatform, PlatformCredentials, QueryResult, ActionResult
```

**BasePlatform Class:**

```python
class BasePlatform(ABC):
    def __init__(self, credentials: PlatformCredentials, platform_type: PlatformType)
    
    @abstractmethod
    async def connect(self) -> bool
    @abstractmethod
    async def disconnect(self) -> bool
    @abstractmethod
    async def validate_credentials(self) -> bool
    @abstractmethod
    async def get_schema(self, object_type: Optional[str] = None) -> Dict[str, Any]
    @abstractmethod
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult
    @abstractmethod
    async def execute_action(self, action_type: ActionType, parameters: Dict[str, Any]) -> ActionResult
    @abstractmethod
    async def search_records(self, object_type: str, criteria: Dict[str, Any]) -> QueryResult
    @abstractmethod
    async def create_record(self, object_type: str, data: Dict[str, Any]) -> ActionResult
    @abstractmethod
    async def update_record(self, object_type: str, record_id: str, data: Dict[str, Any]) -> ActionResult
    @abstractmethod
    async def delete_record(self, object_type: str, record_id: str) -> ActionResult
    
    def get_platform_info(self) -> Dict[str, Any]
    async def health_check(self) -> Dict[str, Any]
```

**Data Classes:**

```python
@dataclass
class PlatformCredentials:
    username: str
    password: str
    api_key: Optional[str] = None
    security_token: Optional[str] = None
    instance_url: Optional[str] = None
    environment: str = "production"

@dataclass
class QueryResult:
    data: List[Dict[str, Any]]
    total_count: int
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0

@dataclass
class ActionResult:
    success: bool
    record_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
```

#### `enterprise_sandbox.platforms.factory`

```python
from enterprise_sandbox.platforms.factory import PlatformFactory, PlatformRegistry
```

**PlatformFactory Class:**

```python
class PlatformFactory:
    @classmethod
    def create_platform(cls, platform_name: str, credentials: PlatformCredentials) -> BasePlatform
    @classmethod
    def register_platform(cls, name: str, platform_class: type)
    @classmethod
    def get_supported_platforms(cls) -> List[str]
```

**PlatformRegistry Class:**

```python
class PlatformRegistry:
    def __init__(self)
    async def register_platform(self, name: str, credentials: PlatformCredentials) -> bool
    async def get_platform(self, name: str) -> Optional[BasePlatform]
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]
    async def disconnect_all(self)
```

### Agent Framework

#### `enterprise_sandbox.agents.base.agent`

```python
from enterprise_sandbox.agents.base.agent import BaseAgent
```

**BaseAgent Class:**

```python
class BaseAgent(ABC):
    def __init__(self, model: str, **kwargs)
    
    @abstractmethod
    def act(self, env, task_index: int) -> float
    @abstractmethod
    def get_messages(self) -> List[Dict[str, str]]
    
    def reset(self, args: Dict[str, Any])
    def get_info(self) -> Dict[str, Any]
```

#### `enterprise_sandbox.agents.single_platform.react_agent`

```python
from enterprise_sandbox.agents.single_platform.react_agent import ReActAgent
```

**ReActAgent Class:**

```python
class ReActAgent(BaseAgent):
    def __init__(self, model: str, schema_obj: dict, max_turns: int = 20, 
                 eval_mode: str = "default", strategy: str = "react", 
                 provider: str = "openai", interactive: bool = False, 
                 agent_type: str = "internal", privacy_aware_prompt: bool = False)
    
    def _build_schema(self, schema_obj: dict) -> str
    def _build_system_prompt(self, schema: str) -> str
    def message_action_parser(self, message: Dict[str, str], model_name: str) -> Dict[str, str]
```

#### `enterprise_sandbox.agents.cross_platform.orchestration_agent`

```python
from enterprise_sandbox.agents.cross_platform.orchestration_agent import OrchestrationAgent
```

**OrchestrationAgent Class:**

```python
class OrchestrationAgent(BaseAgent):
    def __init__(self, model: str, platforms: List[str], strategy: str = "orchestration", **kwargs)
    
    def execute_cross_platform_task(self, task: CrossPlatformTask) -> Dict[str, Any]
    def coordinate_platforms(self, step: TaskStep) -> Any
    def _resolve_dependencies(self, steps: List[TaskStep]) -> List[TaskStep]
    def _execute_step(self, step: TaskStep, context: Dict[str, Any]) -> Any
```

### Environment Framework

#### `enterprise_sandbox.environments.base.environment`

```python
from enterprise_sandbox.environments.base.environment import BaseEnvironment
```

**BaseEnvironment Class:**

```python
class BaseEnvironment(ABC):
    def __init__(self, tasks: Dict[int, Dict], **kwargs)
    
    @abstractmethod
    def reset(self, task_index: int) -> Tuple[str, Dict[str, Any]]
    @abstractmethod
    def step(self, action: Dict[str, Any]) -> Tuple[str, float, bool, Dict[str, Any]]
    
    def get_task(self, task_index: int) -> Dict[str, Any]
    def get_available_tasks(self) -> List[int]
```

#### `enterprise_sandbox.environments.single_platform.chat_env`

```python
from enterprise_sandbox.environments.single_platform.chat_env import ChatEnvironment
```

**ChatEnvironment Class:**

```python
class ChatEnvironment(BaseEnvironment):
    def __init__(self, tasks: Dict[int, Dict], platform: str, 
                 user_model: str = "gpt-4o-2024-08-06", 
                 user_provider: str = "openai", **kwargs)
    
    def reset(self, task_index: int) -> Tuple[str, Dict[str, Any]]
    def step(self, action: Dict[str, Any]) -> Tuple[str, float, bool, Dict[str, Any]]
    def calculate_reward(self) -> Dict[str, Any]
```

#### `enterprise_sandbox.environments.cross_platform.orchestration_env`

```python
from enterprise_sandbox.environments.cross_platform.orchestration_env import OrchestrationEnvironment
```

**OrchestrationEnvironment Class:**

```python
class OrchestrationEnvironment(BaseEnvironment):
    def __init__(self, tasks: Dict[int, Dict], platforms: List[str], 
                 orchestration_engine: OrchestrationEngine, **kwargs)
    
    def reset(self, task_index: int) -> Tuple[str, Dict[str, Any]]
    def step(self, action: Dict[str, Any]) -> Tuple[str, float, bool, Dict[str, Any]]
    def execute_cross_platform_workflow(self, workflow: List[TaskStep]) -> Dict[str, Any]
```

### Orchestration Engine

#### `enterprise_sandbox.orchestration.engine`

```python
from enterprise_sandbox.orchestration.engine import OrchestrationEngine, CrossPlatformTask, TaskStep
```

**OrchestrationEngine Class:**

```python
class OrchestrationEngine:
    def __init__(self, platform_connections: Dict[str, BasePlatform])
    
    async def execute_task(self, task: CrossPlatformTask) -> Dict[str, Any]
    async def _execute_step(self, step: TaskStep, task: CrossPlatformTask) -> Dict[str, Any]
    def _validate_dependencies(self, task: CrossPlatformTask)
    def _topological_sort(self, steps: List[TaskStep], dependencies: Dict[str, List[str]]) -> List[TaskStep]
    def _update_context(self, step: TaskStep, result: Dict[str, Any])
    def _generate_final_result(self, task: CrossPlatformTask) -> Dict[str, Any]
    def _handle_execution_error(self, error: Exception, task: CrossPlatformTask) -> Dict[str, Any]
```

**Data Classes:**

```python
@dataclass
class CrossPlatformTask:
    task_id: str
    name: str
    description: str
    category: str
    platforms: List[str]
    complexity: str
    steps: List[TaskStep]
    dependencies: Dict[str, List[str]]
    expected_output: Any
    evaluation_metric: str
    timeout_seconds: int = 300
    retry_attempts: int = 3

@dataclass
class TaskStep:
    step_id: str
    name: str
    platform: str
    action_type: str
    parameters: Dict[str, Any]
    input_mapping: Dict[str, str]
    output_mapping: Dict[str, str]
    validation_rules: List[ValidationRule]
    error_handling: ErrorHandlingStrategy
    timeout_seconds: int = 60
```

### Configuration Management

#### `enterprise_sandbox.config.config_loader`

```python
from enterprise_sandbox.config.config_loader import PlatformConfigLoader, TaskConfigLoader, AgentConfigLoader
```

**PlatformConfigLoader Class:**

```python
class PlatformConfigLoader:
    def __init__(self, config_path: str = "configs/platform_config.yaml")
    def _load_config(self) -> Dict[str, Any]
    def get_platform_config(self, platform_name: str) -> Dict[str, Any]
    def create_credentials(self, platform_name: str) -> PlatformCredentials
```

**TaskConfigLoader Class:**

```python
class TaskConfigLoader:
    def __init__(self, config_path: str = "configs/task_config.yaml")
    def get_task_config(self, task_type: str) -> Dict[str, Any]
    def get_evaluation_config(self) -> Dict[str, Any]
```

**AgentConfigLoader Class:**

```python
class AgentConfigLoader:
    def __init__(self, config_path: str = "configs/agent_config.yaml")
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]
    def get_model_config(self, model_name: str) -> Dict[str, Any]
```

### Evaluation Framework

#### `enterprise_sandbox.evaluation.evaluators.single_platform_evaluator`

```python
from enterprise_sandbox.evaluation.evaluators.single_platform_evaluator import SinglePlatformEvaluator
```

**SinglePlatformEvaluator Class:**

```python
class SinglePlatformEvaluator:
    def __init__(self, model: str, provider: str)
    
    def evaluate_task(self, task: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, float]
    def _calculate_completion_rate(self, task: Dict[str, Any], result: Dict[str, Any]) -> float
    def _calculate_efficiency(self, task: Dict[str, Any], result: Dict[str, Any]) -> float
    def _calculate_accuracy(self, task: Dict[str, Any], result: Dict[str, Any]) -> float
```

#### `enterprise_sandbox.evaluation.evaluators.cross_platform_evaluator`

```python
from enterprise_sandbox.evaluation.evaluators.cross_platform_evaluator import CrossPlatformEvaluator
```

**CrossPlatformEvaluator Class:**

```python
class CrossPlatformEvaluator:
    def __init__(self, model: str, provider: str)
    
    def evaluate_task(self, task: CrossPlatformTask, execution_result: Dict[str, Any]) -> Dict[str, float]
    def _calculate_coordination_success(self, task: CrossPlatformTask, result: Dict[str, Any]) -> float
    def _calculate_workflow_completion(self, task: CrossPlatformTask, result: Dict[str, Any]) -> float
    def _calculate_data_integrity(self, task: CrossPlatformTask, result: Dict[str, Any]) -> float
    def _calculate_error_recovery(self, task: CrossPlatformTask, result: Dict[str, Any]) -> float
```

### Utility Functions

#### `enterprise_sandbox.utils.helpers`

```python
from enterprise_sandbox.utils.helpers import (
    validate_task_structure,
    parse_natural_language_query,
    format_platform_response,
    calculate_metrics,
    generate_report
)
```

**Functions:**

- `validate_task_structure(task: Dict[str, Any]) -> bool`
  - Validate task structure and required fields
  - Returns: True if valid, raises ValueError if invalid

- `parse_natural_language_query(query: str) -> Dict[str, Any]`
  - Parse natural language query into structured format
  - Returns: Parsed query dictionary

- `format_platform_response(response: Any, platform: str) -> str`
  - Format platform response for consistent display
  - Returns: Formatted response string

- `calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]`
  - Calculate evaluation metrics from results
  - Returns: Dictionary of metrics

- `generate_report(results: List[Dict[str, Any]], output_file: str)`
  - Generate comprehensive evaluation report
  - Saves report to specified file

## Usage Examples

### Basic Platform Usage

```python
from enterprise_sandbox.platforms.factory import PlatformFactory
from enterprise_sandbox.config.config_loader import PlatformConfigLoader

# Load configuration
config = PlatformConfigLoader()
credentials = config.create_credentials("salesforce")

# Create platform instance
platform = PlatformFactory.create_platform("salesforce", credentials)

# Connect and execute query
await platform.connect()
result = await platform.execute_query("SELECT Name FROM Account LIMIT 5")
print(result.data)
```

### Basic Agent Usage

```python
from enterprise_sandbox.agents.single_platform.react_agent import ReActAgent
from enterprise_sandbox.environments.single_platform.chat_env import ChatEnvironment

# Create agent
agent = ReActAgent(
    model="gpt-4o",
    schema_obj=salesforce_schema,
    strategy="react"
)

# Create environment
env = ChatEnvironment(tasks=tasks, platform="salesforce")

# Execute task
reward = agent.act(env, task_index=1)
print(f"Task completed with reward: {reward}")
```

### Cross-Platform Orchestration

```python
from enterprise_sandbox.orchestration.engine import OrchestrationEngine
from enterprise_sandbox.data.assets import get_tasks_by_category

# Get cross-platform task
tasks = get_tasks_by_category("financial_integration")
task = tasks[0]

# Create orchestration engine
engine = OrchestrationEngine(platform_connections)

# Execute cross-platform workflow
result = await engine.execute_task(task)
print(f"Workflow completed: {result}")
```

## Error Handling

### Common Exceptions

```python
from enterprise_sandbox.platforms.base.exceptions import (
    PlatformConnectionError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    OrchestrationError
)
```

**Exception Classes:**

- `PlatformConnectionError`: Raised when platform connection fails
- `AuthenticationError`: Raised when authentication fails
- `RateLimitError`: Raised when API rate limits are exceeded
- `ValidationError`: Raised when input validation fails
- `OrchestrationError`: Raised when cross-platform orchestration fails

### Error Handling Best Practices

```python
try:
    result = await platform.execute_query(query)
except AuthenticationError as e:
    logger.error(f"Authentication failed: {e}")
    # Handle authentication error
except RateLimitError as e:
    logger.warning(f"Rate limit exceeded: {e}")
    # Implement retry logic
except PlatformConnectionError as e:
    logger.error(f"Connection failed: {e}")
    # Handle connection error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected errors
```