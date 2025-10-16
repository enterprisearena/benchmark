# Platform Setup

This guide covers setting up access to each supported enterprise platform for EnterpriseArena.

## Salesforce Setup

### 1. Create a Salesforce Developer Account
- Go to [developer.salesforce.com](https://developer.salesforce.com)
- Sign up for a free Developer Edition account
- Verify your email address

### 2. Create a Connected App
1. In Salesforce Setup, go to **App Manager**
2. Click **New Connected App**
3. Fill in the required fields:
   - **Connected App Name**: EnterpriseArena
   - **API Name**: EnterpriseArena
   - **Contact Email**: your-email@example.com
4. Enable **OAuth Settings**:
   - **Callback URL**: `http://localhost:8080/callback`
   - **Selected OAuth Scopes**: 
     - Access and manage your data (api)
     - Perform requests on your behalf at any time (refresh_token, offline_access)
5. Save and note the **Consumer Key** and **Consumer Secret**

### 3. Create API User
1. Go to **Users** in Setup
2. Create a new user with **System Administrator** profile
3. Generate a **Security Token**:
   - Go to **My Settings** → **Personal** → **Reset My Security Token**
   - Click **Reset Security Token**

### 4. Configure EnterpriseArena
```bash
SALESFORCE_USERNAME=your_api_user@example.com
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
```

## ServiceNow Setup

### 1. Get ServiceNow Instance
- Sign up for a [ServiceNow Developer Instance](https://developer.servicenow.com)
- Note your instance URL (e.g., `https://dev12345.service-now.com`)

### 2. Create API User
1. Navigate to **System Security** → **Users and Groups** → **Users**
2. Create a new user with **admin** role
3. Set a strong password

### 3. Enable REST API
1. Go to **System Definition** → **Plugins**
2. Ensure **REST API** plugin is activated
3. Go to **System Web Services** → **REST** → **REST API Explorer**
4. Test API access with your credentials

### 4. Configure EnterpriseArena
```bash
SERVICENOW_INSTANCE=dev12345
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=your_password
SERVICENOW_INSTANCE_URL=https://dev12345.service-now.com
```

## NetSuite Setup

### 1. Get NetSuite Account
- Sign up for a [NetSuite Developer Account](https://www.netsuite.com/portal/developers/dev-account.shtml)
- Note your account ID and instance URL

### 2. Create Integration Record
1. Go to **Setup** → **Company** → **Enable Features**
2. Enable **SuiteTalk (Web Services)**
3. Go to **Setup** → **Company** → **Integration** → **Manage Integrations**
4. Create new integration:
   - **Name**: EnterpriseArena
   - **State**: Enabled
   - **Token-based Authentication**: Checked
5. Note the **Consumer Key** and **Consumer Secret**

### 3. Create Access Token
1. Go to **Setup** → **Users/Roles** → **Access Tokens**
2. Create new access token:
   - **Application Name**: EnterpriseArena
   - **User**: Select your admin user
   - **Role**: Administrator
3. Note the **Token ID** and **Token Secret**

### 4. Configure EnterpriseArena
```bash
NETSUITE_ACCOUNT_ID=your_account_id
NETSUITE_CONSUMER_KEY=your_consumer_key
NETSUITE_CONSUMER_SECRET=your_consumer_secret
NETSUITE_TOKEN_ID=your_token_id
NETSUITE_TOKEN_SECRET=your_token_secret
NETSUITE_INSTANCE_URL=https://your-account.app.netsuite.com
```

## QuickBooks Setup

### 1. Create QuickBooks App
1. Go to [developer.intuit.com](https://developer.intuit.com)
2. Sign in with your Intuit account
3. Create a new app:
   - **App Name**: EnterpriseArena
   - **App Type**: Web App
   - **Redirect URI**: `http://localhost:8000/callback`
4. Note the **Client ID** and **Client Secret**

### 2. Get Company ID
1. Use the [QuickBooks API Explorer](https://developer.intuit.com/app/developer/qbo/docs/get-started/explore-the-quickbooks-online-api)
2. Connect your QuickBooks Online account
3. Note the **Company ID** from the API response

### 3. Get Refresh Token
1. Use OAuth 2.0 flow to get authorization code
2. Exchange authorization code for access token and refresh token
3. Store the **Refresh Token** securely

### 4. Configure EnterpriseArena
```bash
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_COMPANY_ID=your_company_id
QB_REFRESH_TOKEN=your_refresh_token
QB_REDIRECT_URI=http://localhost:8000/callback
```

## Testing Platform Connections

### Test All Platforms
```bash
python -c "
from enterprise_sandbox.platforms.factory import PlatformFactory
from enterprise_sandbox.config.platform_config import PlatformConfigLoader

config = PlatformConfigLoader()
platforms = ['salesforce', 'servicenow', 'netsuite', 'quickbooks']

for platform_name in platforms:
    try:
        creds = config.create_credentials(platform_name)
        platform = PlatformFactory.create_platform(platform_name, creds)
        success = platform.connect()
        if success:
            print(f'{platform_name}: ✅ Connected successfully')
        else:
            print(f'{platform_name}: ❌ Connection failed')
    except Exception as e:
        print(f'{platform_name}: ❌ Error - {e}')
"
```

### Individual Platform Tests
```bash
# Test Salesforce
python -c "
from simple_salesforce import Salesforce
import os
from dotenv import load_dotenv
load_dotenv()

sf = Salesforce(
    username=os.getenv('SALESFORCE_USERNAME'),
    password=os.getenv('SALESFORCE_PASSWORD'),
    security_token=os.getenv('SALESFORCE_SECURITY_TOKEN')
)
print('Salesforce: ✅ Connected')
"

# Test ServiceNow
python -c "
import requests
import os
from dotenv import load_dotenv
load_dotenv()

response = requests.get(
    f'{os.getenv(\"SERVICENOW_INSTANCE_URL\")}/api/now/table/sys_user?sysparm_limit=1',
    auth=(os.getenv('SERVICENOW_USERNAME'), os.getenv('SERVICENOW_PASSWORD'))
)
if response.status_code == 200:
    print('ServiceNow: ✅ Connected')
else:
    print(f'ServiceNow: ❌ Error {response.status_code}')
"
```

## Troubleshooting

### Common Issues

**Authentication Failures**
- Verify credentials are correct
- Check if accounts are active
- Ensure proper permissions/roles

**Network Connectivity**
- Test platform URLs manually
- Check firewall/proxy settings
- Verify SSL certificates

**API Rate Limits**
- Check platform-specific rate limits
- Implement proper retry logic
- Use connection pooling

**Token Expiration**
- Refresh tokens before expiration
- Implement automatic token renewal
- Monitor token usage

### Getting Help

- Check platform-specific documentation
- Review API logs and error messages
- Test with platform API explorers
- Contact platform support if needed