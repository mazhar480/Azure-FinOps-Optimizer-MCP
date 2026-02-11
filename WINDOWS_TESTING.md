# Windows Testing Guide - Azure FinOps Elite

**Step-by-step guide to run and test the MCP server on Windows**

---

## 📋 Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.10 or higher installed
- ✅ Git (optional, for version control)
- ✅ Azure subscription with appropriate permissions
- ✅ PowerShell or Command Prompt

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Verify Python Installation

```powershell
# Check Python version
python --version
# Should show Python 3.10.x or higher

# Check pip
pip --version
```

If Python is not installed, download from [python.org](https://www.python.org/downloads/).

---

### Step 2: Install Dependencies

```powershell
# Navigate to project directory
cd "e:\References\Azure FinOps Optimizer MCP"

# Install required packages
pip install -r requirements.txt

# Verify installation
pip list | findstr fastmcp
pip list | findstr azure
```

**Expected output:**
```
azure-identity                1.15.0
azure-mgmt-advisor            9.0.0
azure-mgmt-compute            30.0.0
azure-mgmt-consumption        10.0.0
azure-mgmt-costmanagement     4.0.0
azure-mgmt-network            25.0.0
azure-mgmt-resource           23.0.0
fastmcp                       0.2.0
```

---

### Step 3: Configure Environment Variables

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env file with your credentials
notepad .env
```

**Minimum configuration for testing:**
```env
# Azure Authentication (for testing, you can use DefaultAzureCredential)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_SUBSCRIPTION_IDS=your-subscription-id

# Optional: For certificate-based auth
# AZURE_CERTIFICATE_PATH=C:\path\to\cert.pem

# Optional: For Managed Identity (when deployed to Azure)
# USE_MANAGED_IDENTITY=false

# Configuration
ANOMALY_THRESHOLD=1.5
LOG_LEVEL=INFO
```

**To find your Azure credentials:**
```powershell
# Install Azure CLI if not already installed
# Download from: https://aka.ms/installazurecliwindows

# Login to Azure
az login

# Get your tenant ID
az account show --query tenantId -o tsv

# Get your subscription ID
az account show --query id -o tsv

# List all subscriptions
az account list --query "[].{Name:name, ID:id}" -o table
```

---

### Step 4: Test with Examples (No Azure Credentials Required)

```powershell
# Run the examples script (uses mock data if no credentials)
python examples.py
```

**Expected output:**
```
🚀 Azure FinOps Elite - Usage Examples
============================================================

⚠️  Environment not configured!
Please copy .env.example to .env and configure your credentials.

Running with mock data for demonstration purposes...

============================================================
EXAMPLE 1: Anomaly Detection
============================================================
...
```

---

## 🧪 Testing Options

### Option 1: Test Without Azure Credentials (Demo Mode)

Perfect for understanding the tool structure without Azure access.

```powershell
# Run examples with mock data
python examples.py
```

---

### Option 2: Test with Azure CLI Credentials (Easiest)

Uses your Azure CLI login for authentication.

```powershell
# Login to Azure CLI
az login

# Set your .env file to use DefaultAzureCredential
# Leave AZURE_CERTIFICATE_PATH empty

# Run examples
python examples.py
```

---

### Option 3: Test with Service Principal (Production-like)

Most secure option, recommended for production.

#### 3.1 Create Service Principal

```powershell
# Create Service Principal
az ad sp create-for-rbac --name azure-finops-elite --skip-assignment

# Save the output:
# {
#   "appId": "xxx",        # This is AZURE_CLIENT_ID
#   "password": "xxx",     # Not used with certificate
#   "tenant": "xxx"        # This is AZURE_TENANT_ID
# }
```

#### 3.2 Generate Certificate (Optional but Recommended)

**Using OpenSSL (if installed):**
```powershell
# Generate self-signed certificate
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=azure-finops-elite"

# Upload to Service Principal
az ad sp credential reset --name azure-finops-elite --cert @cert.pem --append
```

**Using PowerShell (Windows native):**
```powershell
# Generate self-signed certificate
$cert = New-SelfSignedCertificate `
    -Subject "CN=azure-finops-elite" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -KeySpec Signature `
    -KeyLength 2048 `
    -NotAfter (Get-Date).AddYears(1)

# Export certificate
$certPath = "C:\temp\finops-cert.pfx"
$password = ConvertTo-SecureString -String "YourPassword123!" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $certPath -Password $password

# Convert to PEM (requires OpenSSL or use Azure Key Vault)
# For testing, you can upload the .pfx directly to Azure
```

#### 3.3 Assign RBAC Roles

```powershell
# Get Service Principal Object ID
$spId = az ad sp list --display-name azure-finops-elite --query "[0].id" -o tsv

# Get your subscription ID
$subId = az account show --query id -o tsv

# Assign Cost Management Reader
az role assignment create `
    --assignee $spId `
    --role "Cost Management Reader" `
    --scope "/subscriptions/$subId"

# Assign Reader
az role assignment create `
    --assignee $spId `
    --role "Reader" `
    --scope "/subscriptions/$subId"

# Verify assignments
az role assignment list --assignee $spId --output table
```

#### 3.4 Update .env File

```env
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-app-id
AZURE_CERTIFICATE_PATH=C:\temp\finops-cert.pem
AZURE_SUBSCRIPTION_IDS=your-subscription-id
```

---

## 🔧 Running the MCP Server

### Start the Server

```powershell
# Start the FastMCP server
python server.py
```

**Expected output:**
```
INFO:root:Starting Azure FinOps Elite MCP Server
INFO:root:Log level: INFO
INFO:fastmcp:Server started on stdio
```

### Test Individual Tools

```powershell
# Test anomaly detection
python -c "from tools.anomaly_detector import get_enterprise_anomalies; import json; print(json.dumps(get_enterprise_anomalies(), indent=2))"

# Test CSP audit
python -c "from tools.csp_auditor import csp_tenant_audit; import json; print(json.dumps(csp_tenant_audit(), indent=2))"

# Test budget validation
python -c "from tools.budget_validator import validate_deployment_budget; template = {'resources': []}; import json; print(json.dumps(validate_deployment_budget(template), indent=2))"

# Test governance recommendations
python -c "from tools.governance_advisor import governance_remediation_advisor; import json; print(json.dumps(governance_remediation_advisor(), indent=2))"

# Test executive summary
python -c "from tools.executive_summary import generate_executive_summary; result = generate_executive_summary(); print(result['markdown_report'])"
```

---

## 🧪 Testing with MCP Inspector

The MCP Inspector is a tool for testing MCP servers interactively.

### Install MCP Inspector

```powershell
# Install via npm (requires Node.js)
npm install -g @modelcontextprotocol/inspector

# Or use npx (no installation required)
npx @modelcontextprotocol/inspector
```

### Run with Inspector

```powershell
# Start the server with MCP Inspector
npx @modelcontextprotocol/inspector python server.py
```

This will open a web interface where you can:
- View all available tools
- Test each tool with custom parameters
- See request/response logs
- Debug issues

---

## 🎯 Testing Checklist

### Basic Tests

- [ ] Python installation verified (3.10+)
- [ ] Dependencies installed successfully
- [ ] `.env` file configured
- [ ] `examples.py` runs without errors
- [ ] Server starts with `python server.py`

### Azure Integration Tests

- [ ] Azure CLI login successful (`az login`)
- [ ] Subscription ID retrieved
- [ ] Service Principal created (if using certificate auth)
- [ ] RBAC roles assigned
- [ ] Authentication working (no auth errors in logs)

### Tool Tests

- [ ] Anomaly detection returns data
- [ ] CSP audit identifies resources
- [ ] Budget validation parses templates
- [ ] Governance recommendations retrieved
- [ ] Executive summary generates report
- [ ] Compliance overlay flags recommendations

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastmcp'"

**Solution:**
```powershell
pip install -r requirements.txt
```

---

### Issue: "Authentication failed"

**Solution:**
```powershell
# Verify Azure CLI login
az login
az account show

# Check .env file has correct values
notepad .env

# Test authentication
python -c "from auth import get_credential; cred = get_credential(); print('Auth successful')"
```

---

### Issue: "Permission denied" or "Forbidden"

**Solution:**
```powershell
# Verify RBAC roles are assigned
$spId = az ad sp list --display-name azure-finops-elite --query "[0].id" -o tsv
az role assignment list --assignee $spId --output table

# If missing, assign required roles (see Step 3.3 above)
```

---

### Issue: "Rate limit exceeded"

**Solution:**
- Wait a few minutes and retry
- The tools have built-in retry logic with exponential backoff
- Check `LOG_LEVEL=DEBUG` in `.env` for detailed error messages

---

### Issue: "No cost data returned"

**Possible causes:**
1. Subscription has no recent costs
2. Cost Management API not enabled
3. Insufficient permissions

**Solution:**
```powershell
# Verify Cost Management Reader role is assigned
az role assignment list --assignee $spId --query "[?roleDefinitionName=='Cost Management Reader']" --output table

# Check if subscription has cost data
az consumption usage list --top 1
```

---

## 📊 Sample Test Workflow

```powershell
# 1. Setup
cd "e:\References\Azure FinOps Optimizer MCP"
pip install -r requirements.txt
copy .env.example .env
notepad .env  # Configure your credentials

# 2. Test authentication
python -c "from auth import get_credential; print('Auth OK')"

# 3. Test each tool
python examples.py

# 4. Generate executive summary
python -c "from tools.executive_summary import generate_executive_summary; result = generate_executive_summary(period='monthly'); open('report.md', 'w').write(result['markdown_report']); print('Report saved to report.md')"

# 5. View the report
notepad report.md

# 6. Test one-click setup
python setup_azure_role.py --subscription-id YOUR_SUB_ID --with-script

# 7. Start the server
python server.py
```

---

## 🎓 Next Steps

Once testing is successful:

1. **Deploy to Production**
   - Use Azure Container Apps or App Service
   - Enable Managed Identity
   - Configure monitoring and alerts

2. **Integrate with CI/CD**
   - Add budget validation to pipelines
   - Automate executive reports
   - Set up compliance checks

3. **Schedule Automated Runs**
   - Daily anomaly detection
   - Weekly CSP audits
   - Monthly executive summaries

---

## 📞 Support

If you encounter issues:
1. Check the [README.md](README.md) for general documentation
2. Review [security_guide.md](security_guide.md) for authentication issues
3. See [CUSTOMER_EXPERIENCE.md](CUSTOMER_EXPERIENCE.md) for feature guides

---

**Happy testing! 🚀**
