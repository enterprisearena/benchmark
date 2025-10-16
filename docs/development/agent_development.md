# Agent Development

This guide covers developing agents for EnterpriseArena, including single-platform and cross-platform orchestration agents.

## Agent Architecture

### Base Agent Interface

All agents inherit from the `BaseAgent` class:

```python
from enterprise_sandbox.agents.base.agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, model: str, **kwargs):
        super().__init__(model, **kwargs)
    
    def act(self, env, task_index: int) -> float:
        """Execute a task and return reward (0 or 1)"""
        pass
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Return conversation history"""
        pass
```

## Single-Platform Agents

### ReAct Agent

ReAct (Reasoning + Acting) agents think step-by-step before taking actions:

```python
from enterprise_sandbox.agents.single_platform.react_agent import ReActAgent

class CustomReActAgent(ReActAgent):
    def __init__(self, model: str, schema_obj: dict, **kwargs):
        super().__init__(model, schema_obj, **kwargs)
    
    def _build_system_prompt(self, schema: str) -> str:
        """Customize the system prompt"""
        return f"""
        You are an expert in enterprise software with access to a {self.platform} system.
        
        # Instructions
        - Think step by step before taking actions
        - Use <thought> for reasoning and <execute> for actions
        - Always end with <respond> containing your final answer
        
        # System Schema
        {schema}
        """
```

### Tool-Calling Agent

Tool-calling agents use structured function calls:

```python
from enterprise_sandbox.agents.single_platform.tool_call_agent import ToolCallAgent

class CustomToolCallAgent(ToolCallAgent):
    def __init__(self, model: str, tools: List[Callable], **kwargs):
        super().__init__(model, tools, **kwargs)
    
    def _get_tool_definitions(self) -> List[Dict]:
        """Define available tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_database",
                    "description": "Query the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SQL query"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
```

### Interactive Agent

Interactive agents handle multi-turn conversations:

```python
from enterprise_sandbox.agents.single_platform.interactive_agent import InteractiveAgent

class CustomInteractiveAgent(InteractiveAgent):
    def __init__(self, model: str, **kwargs):
        super().__init__(model, **kwargs)
    
    def handle_user_input(self, user_message: str) -> str:
        """Process user input and generate response"""
        # Custom logic for handling user interactions
        return self._generate_response(user_message)
```

## Cross-Platform Agents

### Orchestration Agent

Orchestration agents coordinate workflows across multiple platforms:

```python
from enterprise_sandbox.agents.cross_platform.orchestration_agent import OrchestrationAgent

class CustomOrchestrationAgent(OrchestrationAgent):
    def __init__(self, model: str, platforms: List[str], **kwargs):
        super().__init__(model, platforms, **kwargs)
    
    def execute_cross_platform_task(self, task: CrossPlatformTask) -> Dict[str, Any]:
        """Execute a cross-platform task"""
        results = {}
        
        # Execute steps in dependency order
        for step in self._resolve_dependencies(task.steps):
            result = self._execute_step(step, results)
            results[step.step_id] = result
        
        return results
    
    def _execute_step(self, step: TaskStep, context: Dict) -> Any:
        """Execute a single step"""
        platform = self.platform_connections[step.platform]
        
        # Resolve parameters using context
        resolved_params = self._resolve_parameters(step.parameters, context)
        
        # Execute action on platform
        if step.action == "query":
            return platform.execute_query(resolved_params["query"])
        elif step.action == "create":
            return platform.create_record(
                resolved_params["object_type"], 
                resolved_params["data"]
            )
        # Add more action types as needed
```

### Workflow Agent

Workflow agents understand complex business processes:

```python
from enterprise_sandbox.agents.cross_platform.workflow_agent import WorkflowAgent

class CustomWorkflowAgent(WorkflowAgent):
    def __init__(self, model: str, **kwargs):
        super().__init__(model, **kwargs)
    
    def understand_workflow(self, task_description: str) -> WorkflowPlan:
        """Parse natural language into workflow plan"""
        # Use LLM to understand the workflow
        workflow_prompt = f"""
        Analyze this business workflow: {task_description}
        
        Break it down into steps with:
        - Platform for each step
        - Action type (query, create, update, delete)
        - Dependencies between steps
        - Data transformations needed
        """
        
        response = self.llm_client.complete(workflow_prompt)
        return self._parse_workflow_plan(response)
    
    def execute_workflow(self, plan: WorkflowPlan) -> Dict[str, Any]:
        """Execute the workflow plan"""
        # Implementation details
        pass
```

## Agent Development Best Practices

### Prompt Engineering

#### System Prompts
- Be specific about the agent's role and capabilities
- Include relevant schema information
- Provide clear examples of expected behavior
- Handle edge cases and error scenarios

#### Few-Shot Examples
```python
def _get_examples(self) -> List[Dict]:
    return [
        {
            "input": "Find all leads created in the last 30 days",
            "output": "<thought>I need to query the Lead object for records created in the last 30 days.</thought>\n<execute>SELECT Name, Email FROM Lead WHERE CreatedDate = LAST_N_DAYS:30</execute>"
        },
        {
            "input": "What is the total value of closed won opportunities?",
            "output": "<thought>I need to sum the Amount field for opportunities with StageName 'Closed Won'.</thought>\n<execute>SELECT SUM(Amount) FROM Opportunity WHERE StageName = 'Closed Won'</execute>"
        }
    ]
```

### Error Handling

```python
def _handle_error(self, error: Exception, context: Dict) -> str:
    """Handle errors gracefully"""
    if isinstance(error, AuthenticationError):
        return "Authentication failed. Please check your credentials."
    elif isinstance(error, RateLimitError):
        return "Rate limit exceeded. Please wait before retrying."
    elif isinstance(error, ValidationError):
        return f"Invalid input: {error.message}"
    else:
        return f"An unexpected error occurred: {str(error)}"
```

### Performance Optimization

#### Caching
```python
from functools import lru_cache

class OptimizedAgent(BaseAgent):
    @lru_cache(maxsize=128)
    def _get_schema(self, object_type: str) -> Dict:
        """Cache schema lookups"""
        return self.platform.get_schema(object_type)
    
    def _batch_queries(self, queries: List[str]) -> List[Dict]:
        """Batch multiple queries for efficiency"""
        # Implementation for batching queries
        pass
```

#### Connection Pooling
```python
class PooledAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connection_pool = ConnectionPool(
            max_connections=10,
            timeout=30
        )
```

## Testing Agents

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

class TestCustomAgent:
    def setup_method(self):
        self.agent = CustomAgent(
            model="gpt-4o",
            schema_obj={"objects": ["Lead", "Account"]}
        )
    
    def test_agent_initialization(self):
        assert self.agent.model == "gpt-4o"
        assert self.agent.schema_obj is not None
    
    @patch('enterprise_sandbox.agents.custom_agent.llm_client')
    def test_simple_query(self, mock_llm):
        mock_llm.complete.return_value = "<execute>SELECT * FROM Lead</execute>"
        
        result = self.agent.act(Mock(), 1)
        assert result in [0, 1]  # Reward should be 0 or 1
    
    def test_error_handling(self):
        with patch.object(self.agent, '_execute_query', side_effect=Exception("Test error")):
            result = self.agent.act(Mock(), 1)
            assert result == 0  # Should return 0 on error
```

### Integration Tests

```python
class TestAgentIntegration:
    def test_salesforce_agent(self):
        """Test agent with real Salesforce connection"""
        agent = SalesforceAgent(
            model="gpt-4o",
            credentials=test_credentials
        )
        
        # Test with real task
        result = agent.act(test_environment, test_task_id)
        assert isinstance(result, (int, float))
    
    def test_cross_platform_workflow(self):
        """Test cross-platform agent workflow"""
        agent = OrchestrationAgent(
            model="gpt-4o",
            platforms=["salesforce", "quickbooks"]
        )
        
        result = agent.execute_cross_platform_task(test_task)
        assert "success" in result
```

## Agent Configuration

### Model Configuration

```python
# configs/agent_config.yaml
agents:
  salesforce_agent:
    model: "gpt-4o"
    strategy: "react"
    max_turns: 20
    temperature: 0.0
    
  cross_platform_agent:
    model: "gpt-4o"
    strategy: "orchestration"
    max_turns: 50
    temperature: 0.1
    platforms: ["salesforce", "servicenow", "quickbooks"]
```

### Environment-Specific Settings

```python
class EnvironmentAwareAgent(BaseAgent):
    def __init__(self, environment: str = "production", **kwargs):
        super().__init__(**kwargs)
        self.environment = environment
        
        if environment == "sandbox":
            self.max_turns = 10  # Shorter for testing
            self.temperature = 0.1
        else:
            self.max_turns = 20
            self.temperature = 0.0
```

## Deployment

### Agent Registry

```python
from enterprise_sandbox.agents.registry import AgentRegistry

# Register custom agents
AgentRegistry.register("custom_react", CustomReActAgent)
AgentRegistry.register("custom_orchestration", CustomOrchestrationAgent)

# Use registered agents
agent = AgentRegistry.create("custom_react", model="gpt-4o")
```

### Monitoring and Logging

```python
import logging
from enterprise_sandbox.utils.monitoring import AgentMonitor

class MonitoredAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.monitor = AgentMonitor()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def act(self, env, task_index: int) -> float:
        start_time = time.time()
        
        try:
            result = super().act(env, task_index)
            self.monitor.record_success(task_index, time.time() - start_time)
            return result
        except Exception as e:
            self.monitor.record_error(task_index, str(e))
            self.logger.error(f"Task {task_index} failed: {e}")
            raise
```

## Contributing Agents

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Include comprehensive docstrings
- Write unit tests for all methods

### Documentation
- Document agent capabilities and limitations
- Provide usage examples
- Include configuration options
- Document any platform-specific requirements

### Performance
- Optimize for common use cases
- Implement proper error handling
- Use appropriate caching strategies
- Monitor resource usage