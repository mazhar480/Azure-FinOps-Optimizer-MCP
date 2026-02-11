"""
Example usage of Azure FinOps Elite MCP Server tools.
This file demonstrates how to use each tool with sample data.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
from utils.logging_config import setup_logging
setup_logging(level="INFO")


def example_anomaly_detection():
    """Example: Detect cost anomalies across subscriptions."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Anomaly Detection")
    print("="*60)
    
    from tools.anomaly_detector import get_enterprise_anomalies
    
    # Detect anomalies with 50% threshold (1.5x average)
    result = get_enterprise_anomalies(threshold=1.5)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total Anomalies: {result['total_anomalies']}")
    print(f"   Excess Spend: ${result['total_excess_spend']:.2f}")
    print(f"   Threshold: {result['threshold']}x")
    
    if result['anomalies']:
        print(f"\n🚨 Top 5 Anomalies:")
        for i, anomaly in enumerate(result['anomalies'][:5], 1):
            print(f"\n   {i}. {anomaly['service_name']}")
            print(f"      Resource Group: {anomaly['resource_group']}")
            print(f"      Actual Cost: ${anomaly['actual_cost']:.2f}")
            print(f"      Average Cost: ${anomaly['average_cost']:.2f}")
            print(f"      Variance: +{anomaly['variance_percent']:.1f}%")


def example_csp_audit():
    """Example: Audit CSP tenants for cost savings."""
    print("\n" + "="*60)
    print("EXAMPLE 2: CSP Tenant Audit")
    print("="*60)
    
    from tools.csp_auditor import csp_tenant_audit
    
    # Audit all configured tenants
    result = csp_tenant_audit()
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n📊 Audit Results:")
    print(f"   Tenants Audited: {result.get('tenants_audited', 1)}")
    print(f"   Total Monthly Savings: ${result['total_monthly_savings']:.2f}")
    print(f"   Total Annual Savings: ${result['total_annual_savings']:.2f}")
    
    # Show findings for first tenant
    if result.get('tenant_results'):
        tenant = result['tenant_results'][0]
        findings = tenant['findings']
        
        print(f"\n💾 Unattached Disks: {len(findings['unattached_disks'])}")
        for disk in findings['unattached_disks'][:3]:
            print(f"   • {disk['disk_name']}: {disk['size_gb']}GB {disk['sku']} - ${disk['monthly_cost']:.2f}/mo")
        
        print(f"\n🌐 Idle Public IPs: {len(findings['idle_public_ips'])}")
        for ip in findings['idle_public_ips'][:3]:
            print(f"   • {ip['ip_name']}: {ip['ip_address']} - ${ip['monthly_cost']:.2f}/mo")


def example_budget_validation():
    """Example: Validate ARM template budget."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Budget Validation")
    print("="*60)
    
    from tools.budget_validator import validate_deployment_budget
    
    # Sample ARM template
    template = {
        "resources": [
            {
                "type": "Microsoft.Compute/virtualMachines",
                "name": "vm-app-01",
                "properties": {
                    "hardwareProfile": {"vmSize": "Standard_D4s_v3"}
                },
                "sku": {}
            },
            {
                "type": "Microsoft.Compute/disks",
                "name": "disk-data-01",
                "properties": {"diskSizeGB": 256},
                "sku": {"name": "Premium_LRS"}
            },
            {
                "type": "Microsoft.Network/publicIPAddresses",
                "name": "pip-app-01",
                "sku": {"name": "Standard"}
            }
        ]
    }
    
    # Validate against $5000/month budget
    result = validate_deployment_budget(template, budget_limit=5000.0, region="eastus")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n📊 Cost Estimate:")
    print(f"   Monthly Cost: ${result['estimated_monthly_cost']:.2f}")
    print(f"   Annual Cost: ${result['estimated_annual_cost']:.2f}")
    print(f"   Budget Limit: ${result['budget_limit']:.2f}")
    print(f"   Within Budget: {'✅ Yes' if result['within_budget'] else '❌ No'}")
    
    print(f"\n💰 Cost Breakdown:")
    for item in result['cost_breakdown']:
        print(f"   • {item['resource_name']}: ${item['monthly_cost']:.2f}/mo ({item['sku']})")
    
    if result['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   • {warning}")


def example_governance_recommendations():
    """Example: Get governance recommendations with risk scoring."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Governance Recommendations")
    print("="*60)
    
    from tools.governance_advisor import governance_remediation_advisor
    
    # Get high-risk recommendations (score 7+)
    result = governance_remediation_advisor(min_risk_score=7)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    summary = result['summary']
    print(f"\n📊 Summary:")
    print(f"   Total Recommendations: {summary['total_recommendations']}")
    print(f"   High Risk (7-10): {summary['high_risk_count']}")
    print(f"   Medium Risk (4-6): {summary['medium_risk_count']}")
    print(f"   Low Risk (1-3): {summary['low_risk_count']}")
    print(f"   Potential Savings: ${summary['potential_monthly_savings']:.2f}/mo")
    
    if result['recommendations']:
        print(f"\n🚨 Top 3 High-Risk Recommendations:")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"\n   {i}. [{rec['category']}] {rec['title']}")
            print(f"      Risk Score: {rec['risk_score']}/10")
            print(f"      ISO 27001: {', '.join(rec['risk_factors']['iso_27001_controls'][:2])}")
            print(f"      Effort: {rec['estimated_effort_hours']} hours")
            print(f"      Cost Impact: ${rec['estimated_cost']:.2f}/mo")


if __name__ == "__main__":
    print("\n" + "🚀 Azure FinOps Elite - Usage Examples")
    print("="*60)
    
    # Check if environment is configured
    if not os.getenv("AZURE_TENANT_ID"):
        print("\n⚠️  Environment not configured!")
        print("Please copy .env.example to .env and configure your credentials.")
        print("\nRunning with mock data for demonstration purposes...\n")
    
    try:
        # Run all examples
        example_anomaly_detection()
        example_csp_audit()
        example_budget_validation()
        example_governance_recommendations()
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nNote: Some examples require valid Azure credentials.")
        print("Configure .env file with your Azure credentials to test with real data.\n")
