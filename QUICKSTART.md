# 🚀 Quick Start - Windows Setup Complete!

**Your Azure FinOps Elite MCP Server is ready to use!**

---

## ✅ What's Been Set Up

1. **Python 3.13.3** - Verified and working
2. **All Dependencies** - Installed successfully
   - FastMCP
   - Azure SDK packages
   - All required tools
3. **Import Tests** - All 7 tools import successfully
4. **Example Script** - Ready to run

---

## 🎯 Next Steps

### Option 1: Test Without Azure Credentials (Demo Mode)

```powershell
# Run examples with mock data
python examples.py
```

This will show you how all the tools work without needing Azure credentials.

---

### Option 2: Connect to Your Azure Subscription

#### Step 1: Login to Azure CLI

```powershell
# Install Azure CLI if not already installed
# Download from: https://aka.ms/installazurecliwindows

# Login
az login

# Verify your subscription
az account show
```

#### Step 2: Configure Environment

```powershell
# The .env file has been created for you
# Edit it with your Azure details
notepad .env
```

Add your Azure credentials:
```env
AZURE_TENANT_ID=your-tenant-id-from-az-account-show
AZURE_CLIENT_ID=your-client-id  # Optional for DefaultAzureCredential
AZURE_SUBSCRIPTION_IDS=your-subscription-id-from-az-account-show

LOG_LEVEL=INFO
ANOMALY_THRESHOLD=1.5
```

#### Step 3: Test with Real Data

```powershell
# Test anomaly detection
python -c "from tools.anomaly_detector import get_enterprise_anomalies; import json; result = get_enterprise_anomalies(); print(json.dumps(result, indent=2))"

# Generate executive summary
python -c "from tools.executive_summary import generate_executive_summary; result = generate_executive_summary(); open('report.md', 'w').write(result['markdown_report']); print('Report saved to report.md')"

# View the report
notepad report.md
```

---

### Option 3: Set Up Service Principal (Production)

For production use with certificate authentication:

```powershell
# Use the one-click setup script
python setup_azure_role.py --subscription-id YOUR_SUB_ID --with-script

# Follow the prompts to:
# 1. Create custom role
# 2. Create service principal
# 3. Assign permissions
```

See `WINDOWS_TESTING.md` for detailed instructions.

---

## 🧪 Quick Tests

### Test All Imports
```powershell
python -c "from tools import anomaly_detector, csp_auditor, budget_validator, governance_advisor, executive_summary, compliance_overlay; print('✅ All tools ready!')"
```

### Test Budget Validation (No Azure Required)
```powershell
python -c "from tools.budget_validator import validate_deployment_budget; template = {'resources': [{'type': 'Microsoft.Compute/virtualMachines', 'name': 'test-vm', 'properties': {'hardwareProfile': {'vmSize': 'Standard_D2s_v3'}}}]}; import json; print(json.dumps(validate_deployment_budget(template, budget_limit=1000.0), indent=2))"
```

### Start the MCP Server
```powershell
python server.py
```

---

## 📚 Documentation

- **[WINDOWS_TESTING.md](WINDOWS_TESTING.md)** - Complete Windows testing guide
- **[README.md](README.md)** - Full documentation
- **[CUSTOMER_EXPERIENCE.md](CUSTOMER_EXPERIENCE.md)** - Customer experience features
- **[security_guide.md](security_guide.md)** - Security and compliance

---

## 🎉 You're All Set!

Your Azure FinOps Elite MCP Server is ready to:
- ✅ Detect cost anomalies
- ✅ Audit CSP tenants
- ✅ Validate deployment budgets
- ✅ Provide governance recommendations
- ✅ Generate executive summaries
- ✅ Check compliance impact
- ✅ Auto-generate Azure roles

**Choose an option above to start testing!**
