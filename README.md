# EnterpriseArena

<div align="center">
<a href="https://github.com/enterprisearena/benchmark"><img src="figures/enterprisearena_logo.png" height="120" ></a>
</div>

<div align="center">
<strong>Multi-Platform Enterprise Software Benchmark</strong>
</div>

EnterpriseArena is a comprehensive benchmark framework for evaluating LLM agents across multiple enterprise software platforms, supporting both single-platform and cross-platform workflows. It extends the success of CRMArena to support complex, multi-system business processes that mirror real-world enterprise scenarios.

## 🌟 Key Features

### Multi-Platform Support
- **Salesforce** (CRM) - Customer relationship management
- **ServiceNow** (ITSM) - IT service management  
- **NetSuite** (ERP) - Enterprise resource planning
- **QuickBooks** (Accounting) - Financial management
- **Extensible Plugin System** - Easy addition of new platforms

### Task Complexity Levels
- **Single-Step Tasks** - Simple operations within one platform
- **Multi-Step Tasks** - Complex workflows within one platform
- **Multi-Turn Tasks** - Interactive conversations with enterprise systems
- **Cross-Platform Tasks** - Workflows spanning multiple enterprise systems

### Cross-Platform Workflows
- **Financial Integration**: QuickBooks ↔ Salesforce (invoice to opportunity)
- **Customer Service**: ServiceNow ↔ Salesforce (incident to case)
- **Sales & Support**: Multi-system coordination
- **Data Synchronization**: Maintain consistency across platforms

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/enterprisearena/benchmark.git
cd benchmark
pip install -e .
```

### Basic Usage

```python
from enterprise_sandbox import EnterpriseArena

# Initialize the framework
arena = EnterpriseArena()

# Register platforms
arena.register_platform('salesforce', salesforce_credentials)
arena.register_platform('quickbooks', quickbooks_credentials)

# Run single-platform task
result = arena.run_single_platform_task('salesforce', 'lead_management')

# Run cross-platform task
result = arena.run_cross_platform_task('invoice_to_opportunity')
```

## 📊 Task Examples

### Single-Platform Tasks

**Salesforce Lead Management**
```python
{
    "query": "Find all leads created in the last 30 days and return their names and email addresses.",
    "answer": ["John Smith, john.smith@email.com", "Jane Doe, jane.doe@email.com"],
    "reward_metric": "exact_match"
}
```

**ServiceNow Incident Management**
```python
{
    "query": "Find all high priority incidents that are still open and return the incident numbers.",
    "answer": ["INC0010001", "INC0010002"],
    "reward_metric": "exact_match"
}
```

### Cross-Platform Tasks

**Invoice to Opportunity Workflow**
```python
{
    "query": "I have a new invoice from QuickBooks for customer 'Acme Corporation' with invoice number INV-2024-001. I need to create a corresponding opportunity in Salesforce and link them together.",
    "answer": ["Opportunity created with ID: 006XX000004DHPY"],
    "platforms": ["quickbooks", "salesforce"],
    "steps": [
        "Fetch invoice from QuickBooks",
        "Transform data for Salesforce format", 
        "Create opportunity in Salesforce",
        "Link records across platforms"
    ]
}
```

## 🏗️ Architecture

### Platform Abstraction Layer
- Unified interface for all enterprise platforms
- Platform-specific implementations with consistent APIs
- Secure credential management and connection pooling
- Health monitoring and error recovery

### Agent Framework
- **Single-Platform Agents**: ReAct, Tool-Calling, Interactive
- **Cross-Platform Orchestration Agents**: Coordinate across multiple systems
- **Workflow Management Agents**: Understand complex business processes

### Orchestration Engine
- Dependency resolution for complex workflows
- Execution context management across platforms
- Error handling and recovery mechanisms
- Performance monitoring and optimization

## 📈 Evaluation Framework

### Metrics
- **Accuracy**: Task completion success rates
- **Efficiency**: Execution time and resource usage
- **Coordination**: Cross-platform workflow success
- **Error Handling**: Graceful failure recovery assessment

### Evaluation Types
- **Single-Platform Evaluation**: Traditional CRMArena-style evaluation
- **Cross-Platform Evaluation**: Multi-system workflow evaluation
- **Integration Testing**: End-to-end workflow validation

## 🔧 Configuration

### Platform Configuration
```yaml
platforms:
  salesforce:
    api_version: "v58.0"
    credentials:
      username: "${SALESFORCE_USERNAME}"
      password: "${SALESFORCE_PASSWORD}"
      security_token: "${SALESFORCE_SECURITY_TOKEN}"
  
  quickbooks:
    environment: "sandbox"
    credentials:
      client_id: "${QB_CLIENT_ID}"
      client_secret: "${QB_CLIENT_SECRET}"
      company_id: "${QB_COMPANY_ID}"
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Platform Setup](docs/platform_setup.md)
- [Task Creation](docs/task_creation.md)
- [Agent Development](docs/agent_development.md)
- [Evaluation Guide](docs/evaluation.md)
- [API Reference](docs/api_reference.md)

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/enterprisearena/benchmark.git
cd benchmark
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built upon the success of [CRMArena](https://github.com/SalesforceAIResearch/CRMArena)
- Inspired by the need for comprehensive enterprise AI evaluation
- Community contributions and feedback

## 📞 Contact

- **Repository**: https://github.com/enterprisearena/benchmark
- **Documentation**: docs/index.md
- **Issues**: https://github.com/enterprisearena/benchmark/issues
- **Email**: contact@enterprisearena.org

## 🗺️ Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [x] Project setup and core framework
- [x] Platform abstraction layer
- [ ] Salesforce integration
- [ ] Basic agent framework

### Phase 2: Multi-Platform Support (Weeks 5-8)
- [ ] ServiceNow integration
- [ ] NetSuite integration
- [ ] QuickBooks integration
- [ ] Multi-platform testing

### Phase 3: Cross-Platform Framework (Weeks 9-12)
- [ ] Cross-platform task framework
- [ ] Orchestration engine
- [ ] Cross-platform agents
- [ ] Cross-platform environments

### Phase 4: Advanced Features (Weeks 13-16)
- [ ] Interactive environments
- [ ] Advanced evaluation
- [ ] Optimization and performance
- [ ] Documentation and examples

### Phase 5: Ecosystem and Extensions (Weeks 17-20)
- [ ] Plugin system
- [ ] Community features
- [ ] Advanced integrations
- [ ] Production readiness

---

<div align="center">
<strong>EnterpriseArena - Advancing Enterprise AI Evaluation</strong>
</div>
