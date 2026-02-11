# Customer Experience Enhancements - Quick Guide

**Three new tools to improve stakeholder communication and deployment experience**

---

## 1. Executive Summary Generator

**Purpose:** Create non-technical FinOps ROI reports for executives and business leaders.

### Usage

```python
from tools.executive_summary import generate_executive_summary

# Generate monthly report
result = generate_executive_summary(period="monthly")

# Save Markdown report
with open("finops_report.md", "w") as f:
    f.write(result['markdown_report'])

# Access summary metrics
print(f"Total savings: ${result['summary_metrics']['total_savings_potential']:,.2f}")
print(f"Anomalies: {result['summary_metrics']['anomaly_count']}")
print(f"High-risk items: {result['summary_metrics']['high_risk_items']}")
```

### Output Example

The generated Markdown report includes:
- **Executive Summary**: Non-technical overview
- **Key Metrics**: Cost anomalies, wasteful resources, security risks
- **Total ROI**: Monthly, annual, and 3-year projections
- **Detailed Findings**: Top anomalies, wasteful resources, security risks
- **Recommended Actions**: Immediate, short-term, and long-term steps

---

## 2. Compliance Overlay

**Purpose:** Flag cost-saving recommendations that may impact ISO 27001 or NIA Qatar compliance.

### Usage

```python
from tools.compliance_overlay import apply_compliance_overlay

# Example cost recommendations
recommendations = [
    {
        "title": "Downgrade to Standard storage",
        "description": "Switch from Premium to Standard SSD to save costs",
        "resource_type": "Microsoft.Compute/disks"
    },
    {
        "title": "Reduce log retention",
        "description": "Reduce log retention from 90 to 30 days",
        "resource_type": "Microsoft.OperationalInsights/workspaces"
    }
]

# Apply compliance overlay
result = apply_compliance_overlay(recommendations)

# Review flagged items
for warning in result['compliance_warnings']:
    print(f"⚠️  {warning['recommendation_title']}")
    print(f"   Severity: {warning['severity']}")
    print(f"   Frameworks: {', '.join(warning['frameworks_impacted'])}")
    print(f"   Action: {warning['action_required']}")
```

### Severity Levels

- **CRITICAL**: Do not implement without compliance officer approval
- **HIGH**: Requires security/compliance team review
- **MEDIUM**: Review impact on compliance controls
- **LOW**: Minimal compliance impact

---

## 3. One-Click Setup Script

**Purpose:** Generate ready-to-use Azure Custom Role JSON with least-privilege access.

### Usage

```bash
# Basic usage
python setup_azure_role.py --subscription-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# With custom role name
python setup_azure_role.py \
  --subscription-id <sub-id> \
  --role-name "My FinOps Role"

# Generate deployment script
python setup_azure_role.py \
  --subscription-id <sub-id> \
  --with-script
```

### Output

1. **finops_custom_role.json**: Azure Custom Role definition
2. **finops_custom_role_deploy.sh**: Deployment script (if --with-script)

### Deployment

```bash
# Option 1: Use generated script
chmod +x finops_custom_role_deploy.sh
./finops_custom_role_deploy.sh

# Option 2: Manual deployment
az role definition create --role-definition finops_custom_role.json
```

---

## Integration Examples

### Weekly Executive Report

```python
# Generate and email weekly report
from tools.executive_summary import generate_executive_summary

result = generate_executive_summary(period="monthly")

# Save report
with open(f"finops_report_{datetime.now().strftime('%Y%m%d')}.md", "w") as f:
    f.write(result['markdown_report'])

# Send to executives
send_email(
    to="executives@company.com",
    subject="Weekly FinOps Report",
    body=result['markdown_report']
)
```

### Compliance-Aware Cost Optimization

```python
# Get CSP audit recommendations
from tools.csp_auditor import csp_tenant_audit
from tools.compliance_overlay import apply_compliance_overlay

audit_result = csp_tenant_audit()

# Extract recommendations
recommendations = []
for disk in audit_result['tenant_results'][0]['findings']['unattached_disks']:
    recommendations.append({
        "title": f"Delete unattached disk {disk['disk_name']}",
        "description": f"Unattached {disk['sku']} disk",
        "resource_type": "Microsoft.Compute/disks"
    })

# Check compliance impact
compliance_result = apply_compliance_overlay(recommendations)

# Implement safe recommendations
for rec in compliance_result['safe_recommendations']:
    print(f"✅ Safe to delete: {rec['title']}")

# Review flagged recommendations
for rec in compliance_result['flagged_recommendations']:
    print(f"⚠️  Requires review: {rec['title']}")
    print(f"   Compliance flags: {len(rec['compliance_flags'])}")
```

### Automated Setup for New Customers

```bash
#!/bin/bash
# Customer onboarding script

CUSTOMER_SUB_ID=$1
CUSTOMER_NAME=$2

echo "Setting up FinOps for $CUSTOMER_NAME..."

# Generate custom role
python setup_azure_role.py \
  --subscription-id $CUSTOMER_SUB_ID \
  --role-name "FinOps-$CUSTOMER_NAME" \
  --with-script

# Deploy role
./finops_custom_role_deploy.sh

# Create Service Principal
az ad sp create-for-rbac --name "finops-$CUSTOMER_NAME" --skip-assignment

# Assign role
az role assignment create \
  --assignee <sp-id> \
  --role "FinOps-$CUSTOMER_NAME" \
  --scope /subscriptions/$CUSTOMER_SUB_ID

echo "✅ Setup complete for $CUSTOMER_NAME"
```

---

## Best Practices

### Executive Summary
- Generate monthly for regular stakeholder updates
- Use annual period for budget planning
- Include in board presentations
- Share with finance teams

### Compliance Overlay
- Always check before implementing cost recommendations
- Review flagged items with security/compliance teams
- Document justifications for proceeding with flagged items
- Use as input for risk assessment

### One-Click Setup
- Use for consistent RBAC across subscriptions
- Version control the generated JSON
- Test in dev/test subscriptions first
- Document any customizations

---

**For detailed information, see the main [README.md](README.md) and [security_guide.md](security_guide.md).**
