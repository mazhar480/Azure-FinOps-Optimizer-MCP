# Security Guide - Azure FinOps Elite

**Enterprise security implementation for ISO 27001 and Zero Trust compliance**

---

## 🔐 Authentication Architecture

### Service Principal with Certificate (Recommended)

**Why Certificate-based Authentication?**
- **ISO 27001 Compliant**: Meets cryptographic control requirements (A.10.1.1, A.10.1.2)
- **Zero Trust**: Stronger than password-based authentication
- **Rotation**: Easier to rotate than client secrets
- **Audit Trail**: Certificate usage is logged in Azure AD

**Certificate Requirements:**
- **Key Type**: RSA
- **Key Size**: Minimum 2048 bits (4096 recommended for high-security environments)
- **Validity**: 1-2 years (with automated rotation)
- **Storage**: Azure Key Vault or Hardware Security Module (HSM)
- **Format**: PEM (.pem) or PFX (.pfx)

---

## 🛠️ Setup Instructions

### 1. Generate Certificate

**Option A: Self-Signed Certificate (Development)**
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/CN=azure-finops-elite/O=YourCompany/C=US"
```

**Option B: Certificate from Azure Key Vault (Production)**
```bash
# Create Key Vault
az keyvault create --name finops-kv --resource-group finops-rg --location eastus

# Generate certificate in Key Vault
az keyvault certificate create \
  --vault-name finops-kv \
  --name finops-cert \
  --policy "$(az keyvault certificate get-default-policy)"

# Download certificate
az keyvault certificate download \
  --vault-name finops-kv \
  --name finops-cert \
  --file cert.pem
```

---

### 2. Create Service Principal

```bash
# Create Service Principal
az ad sp create-for-rbac --name azure-finops-elite --skip-assignment

# Output:
# {
#   "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  # AZURE_CLIENT_ID
#   "displayName": "azure-finops-elite",
#   "password": "...",  # Not used with certificate
#   "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # AZURE_TENANT_ID
# }

# Upload certificate to Service Principal
az ad sp credential reset \
  --name azure-finops-elite \
  --cert @cert.pem \
  --append
```

---

### 3. Assign RBAC Roles (Least-Privilege)

**Required Roles:**

```bash
# Get Service Principal Object ID
SP_ID=$(az ad sp list --display-name azure-finops-elite --query "[0].id" -o tsv)

# Assign Cost Management Reader (for cost data)
az role assignment create \
  --assignee $SP_ID \
  --role "Cost Management Reader" \
  --scope /subscriptions/<subscription-id>

# Assign Reader (for resource metadata)
az role assignment create \
  --assignee $SP_ID \
  --role "Reader" \
  --scope /subscriptions/<subscription-id>

# Assign Advisor Reader (for recommendations)
az role assignment create \
  --assignee $SP_ID \
  --role "Advisor Reader" \
  --scope /subscriptions/<subscription-id>
```

**Verify Permissions:**
```bash
az role assignment list --assignee $SP_ID --output table
```

---

### 4. Configure Environment

```bash
# Create .env file
cat > .env << EOF
# Azure Authentication
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CERTIFICATE_PATH=/path/to/cert.pem
AZURE_CERTIFICATE_PASSWORD=  # Leave empty if no password

# Subscription Configuration
AZURE_SUBSCRIPTION_IDS=sub-id-1,sub-id-2,sub-id-3

# Optional: CSP Configuration
CSP_TENANT_IDS=tenant-id-1,tenant-id-2

# Tool Configuration
ANOMALY_THRESHOLD=1.5
CACHE_TTL_SECONDS=300
LOG_LEVEL=INFO
EOF

# Secure the .env file
chmod 600 .env
```

---

## 🔒 Zero Trust Implementation

### Principle 1: Verify Explicitly

**Implementation:**
- Certificate-based authentication (cryptographic proof)
- Token validation on every request
- Correlation IDs for request tracing

**Code Example:**
```python
# auth.py validates credentials before any API call
credential = get_credential()
token = credential.get_token("https://management.azure.com/.default")
# Token is verified by Azure AD before granting access
```

---

### Principle 2: Use Least Privilege Access

**Implementation:**
- Read-only RBAC roles (no write permissions)
- Subscription-scoped (not management group or tenant)
- Minimal API permissions

**RBAC Policy:**
```json
{
  "permissions": [{
    "actions": [
      "Microsoft.Consumption/*/read",
      "Microsoft.CostManagement/*/read",
      "Microsoft.Advisor/*/read",
      "Microsoft.Resources/subscriptions/read",
      "Microsoft.Compute/disks/read",
      "Microsoft.Network/publicIPAddresses/read"
    ],
    "notActions": [],  // No write permissions
    "dataActions": [],
    "notDataActions": []
  }]
}
```

---

### Principle 3: Assume Breach

**Implementation:**
- Comprehensive audit logging
- Correlation IDs for incident investigation
- Rate limiting and retry logic
- No sensitive data in logs

**Logging Example:**
```python
# All requests are logged with correlation IDs
logger.info(f"[{correlation_id}] Querying cost data for subscription {sub_id[:8]}...")
# Logs: timestamp=2026-02-11T12:00:00Z level=INFO correlation_id=abc-123 message=...
```

---

## 📋 ISO 27001 Compliance

### Control Mappings

| ISO 27001 Control | Implementation | Evidence |
|-------------------|----------------|----------|
| **A.9.1.1** - Access control policy | Least-privilege RBAC roles | `policy.json` |
| **A.9.2.1** - User registration | Service Principal with certificate | Setup scripts |
| **A.9.4.1** - Information access restriction | Read-only permissions | RBAC assignments |
| **A.10.1.1** - Cryptographic controls | Certificate-based auth (RSA 2048+) | Certificate generation |
| **A.12.4.1** - Event logging | Structured logging with correlation IDs | `logging_config.py` |
| **A.18.1.1** - Legal compliance | NIA Qatar framework integration | `governance_advisor.py` |

---

### Audit Logging

**What is Logged:**
- All API requests (with correlation IDs)
- Authentication events (success/failure)
- Rate limit errors
- Cost anomalies detected
- Governance recommendations

**Log Format:**
```
timestamp=2026-02-11T12:00:00Z level=INFO logger=tools.anomaly_detector correlation_id=abc-123 message=Starting anomaly detection
```

**Log Retention:**
- Minimum 90 days (configurable)
- Store in centralized logging system (Azure Monitor, Splunk, etc.)

---

## 🌍 NIA Qatar Framework Compliance

### Data Sovereignty
- **Requirement**: Data must be stored in Qatar or approved regions
- **Implementation**: Configure `region` parameter in budget validation
- **Verification**: Check Azure region compliance in Azure Portal

### Encryption at Rest
- **Requirement**: All data must be encrypted at rest
- **Implementation**: Governance advisor detects unencrypted resources
- **Risk Score**: +2 for encryption violations

### Encryption in Transit
- **Requirement**: All data must be encrypted in transit
- **Implementation**: All Azure API calls use HTTPS (TLS 1.2+)
- **Verification**: Azure SDK enforces HTTPS

### Access Logging
- **Requirement**: All access must be logged and monitored
- **Implementation**: Structured logging with correlation IDs
- **Retention**: 90+ days in Azure Monitor

### Multi-Factor Authentication
- **Requirement**: MFA required for administrative access
- **Implementation**: Certificate-based auth (cryptographic MFA)
- **Verification**: Governance advisor detects MFA violations

---

## 🔄 Certificate Rotation

**Recommended Schedule:** Every 12 months

**Rotation Process:**
```bash
# 1. Generate new certificate
openssl req -x509 -newkey rsa:2048 -keyout key-new.pem -out cert-new.pem -days 365 -nodes

# 2. Upload new certificate (append, don't replace)
az ad sp credential reset --name azure-finops-elite --cert @cert-new.pem --append

# 3. Update .env file
AZURE_CERTIFICATE_PATH=/path/to/cert-new.pem

# 4. Restart application
python server.py

# 5. Verify new certificate works
# Test all tools

# 6. Remove old certificate
az ad sp credential delete --name azure-finops-elite --key-id <old-key-id>
```

---

## 🚨 Incident Response

### Authentication Failure

**Symptoms:**
- `ClientAuthenticationError: Authentication failed`
- 401 Unauthorized errors

**Response:**
1. Check certificate expiration: `openssl x509 -in cert.pem -noout -dates`
2. Verify Service Principal exists: `az ad sp show --id <client-id>`
3. Check RBAC assignments: `az role assignment list --assignee <sp-id>`
4. Review Azure AD sign-in logs for failures

---

### Compromised Credentials

**Symptoms:**
- Unexpected API calls in audit logs
- Certificate used from unauthorized IP addresses

**Response:**
1. **Immediate**: Revoke certificate: `az ad sp credential delete --name azure-finops-elite --key-id <key-id>`
2. **Investigate**: Review Azure AD sign-in logs and audit logs
3. **Remediate**: Generate new certificate and rotate
4. **Document**: Create incident report with timeline and root cause

---

## 📊 Security Monitoring

### Metrics to Track

1. **Authentication Success Rate**: Should be >99%
2. **Rate Limit Errors**: Should be <1% of requests
3. **Certificate Expiration**: Alert 30 days before expiry
4. **Anomaly Detection**: Track false positive rate
5. **Governance Risk Score**: Track trend over time

### Alerting

**Azure Monitor Alerts:**
```bash
# Alert on authentication failures
az monitor metrics alert create \
  --name finops-auth-failures \
  --resource-group finops-rg \
  --scopes /subscriptions/<sub-id> \
  --condition "count > 5" \
  --description "FinOps authentication failures"
```

---

## ✅ Security Checklist

- [ ] Certificate generated with RSA 2048+ bits
- [ ] Certificate stored in Azure Key Vault or HSM
- [ ] Service Principal created with certificate authentication
- [ ] Least-privilege RBAC roles assigned (Cost Management Reader, Reader, Advisor Reader)
- [ ] `.env` file secured with `chmod 600`
- [ ] Audit logging enabled and centralized
- [ ] Certificate rotation scheduled (every 12 months)
- [ ] Incident response plan documented
- [ ] Security monitoring and alerting configured
- [ ] ISO 27001 control mappings documented
- [ ] NIA Qatar compliance verified

---

## 📞 Support

For security questions or incident reporting, contact: security@yourcompany.com

---

**Security is a shared responsibility. Stay vigilant! 🛡️**
