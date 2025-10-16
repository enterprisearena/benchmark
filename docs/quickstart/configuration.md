# Configuration

## Environment Variables

EnterpriseArena uses environment variables for configuration. Copy `env.example` to `.env` and fill in your credentials.

### Platform Credentials

#### Salesforce
```bash
SALESFORCE_USERNAME=your_salesforce_username
SALESFORCE_PASSWORD=your_salesforce_password
SALESFORCE_SECURITY_TOKEN=your_security_token
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
```

#### ServiceNow
```bash
SERVICENOW_INSTANCE=your-instance
SERVICENOW_USERNAME=your_servicenow_username
SERVICENOW_PASSWORD=your_servicenow_password
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
```

#### NetSuite
```bash
NETSUITE_ACCOUNT_ID=your_netsuite_account_id
NETSUITE_CONSUMER_KEY=your_netsuite_consumer_key
NETSUITE_CONSUMER_SECRET=your_netsuite_consumer_secret
NETSUITE_TOKEN_ID=your_netsuite_token_id
NETSUITE_TOKEN_SECRET=your_netsuite_token_secret
NETSUITE_INSTANCE_URL=https://your-instance.app.netsuite.com
```

#### QuickBooks
```bash
QB_CLIENT_ID=your_quickbooks_client_id
QB_CLIENT_SECRET=your_quickbooks_client_secret
QB_COMPANY_ID=your_quickbooks_company_id
QB_REFRESH_TOKEN=your_quickbooks_refresh_token
QB_REDIRECT_URI=http://localhost:8000/callback
```

### LLM Provider Credentials

#### OpenAI
```bash
OPENAI_API_KEY=your_openai_api_key
```

#### Anthropic
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
```

#### Google
```bash
GOOGLE_API_KEY=your_google_api_key
```

#### AWS Bedrock
```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

#### Together AI
```bash
TOGETHER_API_KEY=your_together_api_key
```

## Configuration Files

### Platform Configuration (configs/platform_config.yaml)

```yaml
platforms:
  salesforce:
    type: "crm"
    api_version: "v58.0"
    environment: "sandbox"  # production, sandbox
    credentials:
      username: "${SALESFORCE_USERNAME}"
      password: "${SALESFORCE_PASSWORD}"
      security_token: "${SALESFORCE_SECURITY_TOKEN}"
    connection_pool:
      max_connections: 10
      timeout: 30
  
  servicenow:
    type: "itsm"
    instance: "${SERVICENOW_INSTANCE}"
    api_version: "v2"
    credentials:
      username: "${SERVICENOW_USERNAME}"
      password: "${SERVICENOW_PASSWORD}"
```

### Task Configuration (configs/task_config.yaml)

```yaml
tasks:
  single_platform:
    max_turns: 20
    timeout: 300
    retry_attempts: 3
  
  cross_platform:
    max_turns: 50
    timeout: 600
    retry_attempts: 5
    orchestration_timeout: 30
```

### Agent Configuration (configs/agent_config.yaml)

```yaml
agents:
  default_model: "gpt-4o"
  default_strategy: "react"
  max_tokens: 2000
  temperature: 0.0
  
  strategies:
    react:
      max_turns: 20
      thinking_enabled: true
    
    tool_call:
      max_turns: 15
      tool_timeout: 30
    
    orchestration:
      max_turns: 50
      step_timeout: 60
```

## Security Best Practices

### Credential Management
- Never commit `.env` files to version control
- Use environment-specific credential files
- Rotate credentials regularly
- Use least-privilege access principles

### Network Security
- Use HTTPS for all API communications
- Configure proper firewall rules
- Use VPN for sensitive environments
- Monitor API usage and access logs

### Data Privacy
- Use sandbox environments for testing
- Anonymize sensitive data in logs
- Implement data retention policies
- Follow GDPR/CCPA compliance requirements

## Validation

### Test Configuration
```bash
# Test platform connections
python -c "
from enterprise_sandbox.platforms.factory import PlatformFactory
from enterprise_sandbox.config.platform_config import PlatformConfigLoader

config = PlatformConfigLoader()
for platform in ['salesforce', 'servicenow']:
    try:
        creds = config.create_credentials(platform)
        print(f'{platform}: ✅ Credentials loaded')
    except Exception as e:
        print(f'{platform}: ❌ {e}')
"
```

### Verify Environment
```bash
# Check all environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = [
    'SALESFORCE_USERNAME', 'SALESFORCE_PASSWORD',
    'SERVICENOW_INSTANCE', 'SERVICENOW_USERNAME',
    'OPENAI_API_KEY'
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f'{var}: ✅ Set')
    else:
        print(f'{var}: ❌ Missing')
"
```