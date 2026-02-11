# FinOps Agent Usage Guide

**How to use Azure FinOps Elite MCP Server for proactive cost optimization**

---

## 🎯 Overview

The FinOps Agent is an AI-powered assistant that uses the Azure FinOps Elite MCP Server to automate cost optimization, governance, and compliance workflows. This guide explains how to leverage the four core tools to maximize savings and reduce operational overhead.

---

## 🔄 Recommended Workflows

### Daily: Anomaly Detection

**Goal:** Catch unexpected spend spikes before they impact your budget.

**Workflow:**
```
1. Morning (9 AM): Run detect_anomalies with threshold=1.5
2. Review anomalies sorted by variance_percent
3. For each high-variance item:
   - Investigate root cause (new deployments, scaling events, etc.)
   - Create incident ticket if unexpected
   - Notify resource owner
4. Track excess spend trends over time
```

**Example Agent Prompt:**
```
"Check for cost anomalies in all subscriptions. 
For any anomalies over $500, investigate the resource group 
and notify me with details."
```

**Expected Output:**
- List of anomalies with actual vs. average costs
- Total excess spend across all subscriptions
- Variance percentages for prioritization

---

### Weekly: CSP Tenant Audit

**Goal:** Identify quick wins for cost savings across customer environments.

**Workflow:**
```
1. Monday morning: Run audit_csp_tenants for all delegated tenants
2. Generate savings report by tenant
3. For each tenant with >$100/month savings potential:
   - Create cleanup task list
   - Schedule customer review meeting
   - Document findings in CRM
4. Execute approved cleanups
5. Track realized savings
```

**Example Agent Prompt:**
```
"Audit all CSP tenants and create a prioritized list of 
cost optimization opportunities. For tenants with >$200/month 
savings, draft an email to the customer with recommendations."
```

**Expected Output:**
- Unattached disks by tenant (with size, SKU, cost)
- Idle public IPs by tenant
- Total monthly and annual savings potential
- Prioritized action list

---

### Pre-Deployment: Budget Validation

**Goal:** Prevent cost overruns by validating infrastructure costs before deployment.

**Workflow:**
```
1. CI/CD Pipeline Integration:
   - Extract ARM/Bicep template from PR
   - Run validate_budget with team's monthly budget limit
   - Block PR if budget exceeded
   - Add cost estimate as PR comment
2. Manual Review:
   - Review cost breakdown by resource type
   - Check warnings for premium SKUs
   - Approve or request optimization
```

**Example Agent Prompt:**
```
"Validate this ARM template against a $5000 monthly budget. 
If it exceeds the budget, suggest cost optimizations like 
switching to Standard SKUs or reducing VM sizes."
```

**Expected Output:**
- Estimated monthly and annual costs
- Cost breakdown by resource
- Budget validation (within/exceeded)
- Warnings for expensive resources

---

### Monthly: Governance & Compliance Review

**Goal:** Prioritize security and compliance remediation by business impact.

**Workflow:**
```
1. First Monday of month: Run get_governance_recommendations with min_risk_score=7
2. Review high-risk recommendations (score 7-10)
3. For each recommendation:
   - Assess ISO 27001 and NIA Qatar impact
   - Estimate remediation effort
   - Assign to responsible team
   - Add to sprint backlog
4. Track remediation progress
5. Re-run at end of month to measure improvement
```

**Example Agent Prompt:**
```
"Get all high-risk governance recommendations (score 7+). 
Create a prioritized remediation plan with effort estimates 
and assign to the appropriate teams based on ISO 27001 controls."
```

**Expected Output:**
- Prioritized recommendations by risk score
- ISO 27001 and NIA Qatar mappings
- Remediation steps and effort estimates
- Potential cost savings from compliance

---

## 🤖 Agent Integration Patterns

### Slack/Teams Notifications

**Use case:** Automated daily anomaly alerts

```python
# Pseudo-code for Slack integration
anomalies = detect_anomalies(threshold=1.5)

if anomalies['total_anomalies'] > 0:
    message = f"🚨 Cost Alert: {anomalies['total_anomalies']} anomalies detected\n"
    message += f"💰 Excess spend: ${anomalies['total_excess_spend']}\n\n"
    
    for anomaly in anomalies['anomalies'][:5]:
        message += f"• {anomaly['service_name']}: ${anomaly['actual_cost']} "
        message += f"(+{anomaly['variance_percent']}%)\n"
    
    slack_client.post_message(channel='#finops-alerts', text=message)
```

---

### ServiceNow Ticket Creation

**Use case:** Automated governance remediation tickets

```python
# Pseudo-code for ServiceNow integration
recommendations = get_governance_recommendations(min_risk_score=8)

for rec in recommendations['recommendations']:
    if rec['risk_score'] >= 8:
        servicenow.create_ticket(
            title=rec['title'],
            description=rec['description'],
            priority='High' if rec['risk_score'] >= 9 else 'Medium',
            assigned_to=get_owner_from_iso_control(rec['risk_factors']['iso_27001_controls']),
            custom_fields={
                'risk_score': rec['risk_score'],
                'iso_controls': ', '.join(rec['risk_factors']['iso_27001_controls']),
                'estimated_effort': rec['estimated_effort_hours']
            }
        )
```

---

### CI/CD Pipeline Integration

**Use case:** Pre-deployment cost gates

```yaml
# GitHub Actions example
name: Cost Validation
on: [pull_request]

jobs:
  validate-cost:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Extract ARM template
        run: az bicep build --file main.bicep --outfile template.json
      
      - name: Validate budget
        run: |
          python -c "
          import json
          from tools.budget_validator import validate_deployment_budget
          
          with open('template.json') as f:
              template = json.load(f)
          
          result = validate_deployment_budget(template, budget_limit=5000.0)
          
          if not result['within_budget']:
              print(f'❌ Budget exceeded: ${result['estimated_monthly_cost']}')
              exit(1)
          else:
              print(f'✅ Within budget: ${result['estimated_monthly_cost']}')
          "
```

---

## 📊 Reporting & Dashboards

### Weekly Cost Optimization Report

**Combine multiple tools for comprehensive insights:**

```python
# Weekly report generation
report = {
    'week': datetime.now().strftime('%Y-W%U'),
    'anomalies': detect_anomalies(threshold=1.5),
    'csp_audit': audit_csp_tenants(),
    'governance': get_governance_recommendations(min_risk_score=5)
}

# Calculate KPIs
total_savings_potential = (
    report['csp_audit']['total_monthly_savings'] +
    report['governance']['summary']['potential_monthly_savings']
)

# Generate executive summary
summary = f"""
FinOps Weekly Report - Week {report['week']}

📈 Cost Anomalies: {report['anomalies']['total_anomalies']} detected
💰 Excess Spend: ${report['anomalies']['total_excess_spend']}

🏢 CSP Tenant Audit:
   - Unattached Resources: {len(report['csp_audit']['tenant_results'][0]['findings']['unattached_disks'])} disks, 
     {len(report['csp_audit']['tenant_results'][0]['findings']['idle_public_ips'])} IPs
   - Monthly Savings: ${report['csp_audit']['total_monthly_savings']}

🛡️ Governance:
   - High-Risk Items: {report['governance']['summary']['high_risk_count']}
   - Compliance Savings: ${report['governance']['summary']['potential_monthly_savings']}

💡 Total Savings Potential: ${total_savings_potential}/month (${total_savings_potential * 12}/year)
"""

# Send to stakeholders
send_email(to='finops-team@company.com', subject='Weekly FinOps Report', body=summary)
```

---

## 🎓 Best Practices

### 1. Start Small, Scale Gradually
- Begin with one subscription for anomaly detection
- Validate results before expanding to all subscriptions
- Tune threshold based on your environment (start at 1.5, adjust as needed)

### 2. Automate Repetitive Tasks
- Schedule daily anomaly checks via cron/Azure Functions
- Integrate budget validation into CI/CD pipelines
- Auto-create tickets for high-risk governance items

### 3. Combine Tools for Maximum Impact
- Use anomaly detection to find problems
- Use CSP audit to find quick wins
- Use budget validation to prevent future issues
- Use governance advisor to improve security posture

### 4. Track Metrics Over Time
- Anomaly frequency and severity trends
- Realized savings from CSP audits
- Governance risk score improvements
- Budget validation pass/fail rates

### 5. Collaborate Across Teams
- Share anomaly reports with DevOps teams
- Involve security teams in governance remediation
- Engage finance teams in budget validation
- Partner with customers on CSP audit findings

---

## 🚀 Advanced Use Cases

### Multi-Region Cost Comparison
```python
# Compare costs across regions for migration planning
regions = ['eastus', 'westeurope', 'southeastasia']
template = load_arm_template('infrastructure.json')

for region in regions:
    result = validate_budget(template, region=region)
    print(f"{region}: ${result['estimated_monthly_cost']}/month")
```

### Automated Remediation
```python
# Auto-delete unattached disks older than 90 days
audit_result = audit_csp_tenants()

for disk in audit_result['tenant_results'][0]['findings']['unattached_disks']:
    created_date = datetime.strptime(disk['created_date'], '%Y-%m-%d')
    age_days = (datetime.now() - created_date).days
    
    if age_days > 90:
        # Delete disk (with approval workflow)
        print(f"Deleting disk {disk['disk_name']} (age: {age_days} days)")
        # az disk delete --ids {disk['id']} --yes
```

### Custom Risk Scoring
```python
# Extend governance advisor with custom business rules
recommendations = get_governance_recommendations(min_risk_score=1)

for rec in recommendations['recommendations']:
    # Add custom scoring based on resource tags
    if 'production' in rec['impacted_resource'].lower():
        rec['risk_score'] += 2  # Increase risk for production resources
    
    if rec['category'] == 'Cost' and rec['estimated_cost'] > 5000:
        rec['risk_score'] += 3  # Prioritize high-cost items
```

---

## 📞 Support

For questions or advanced integration scenarios, please refer to the [README](README.md) or open an issue on GitHub.

---

**Happy optimizing! 💰**
