# Installation

## Prerequisites

- Python 3.8 or higher
- Git
- Access to enterprise platform sandboxes (Salesforce, ServiceNow, NetSuite, QuickBooks)
- LLM provider API keys (OpenAI, Anthropic, Google, etc.)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/enterprisearena/benchmark.git
cd benchmark
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

### 4. Set Up Environment Configuration

```bash
cp env.example .env
```

### 5. Configure Your Credentials

Edit the `.env` file with your platform and LLM provider credentials:

```bash
# Salesforce
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token

# ServiceNow
SERVICENOW_INSTANCE=your-instance
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password

# LLM Provider
OPENAI_API_KEY=your_openai_key
```

### 6. Verify Installation

```bash
python -c "from enterprise_sandbox import ALL_TASKS; print(f'Loaded {len(ALL_TASKS)} tasks')"
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'enterprise_sandbox'**
- Ensure you're in the correct directory
- Run `pip install -e .` again

**Authentication Errors**
- Verify your credentials in `.env`
- Check that your platform sandboxes are accessible
- Ensure API keys are valid and have proper permissions

**Network Issues**
- Check firewall settings
- Verify proxy configuration if applicable
- Test platform connectivity manually

### Getting Help

- Check the [Configuration Guide](configuration.md) for detailed setup
- Review [Platform Setup](platform_setup.md) for platform-specific instructions
- Open an issue on [GitHub](https://github.com/enterprisearena/benchmark/issues)