"""
Azure FinOps Elite MCP Server
Production-grade FinOps automation for Enterprise and CSP environments.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from fastmcp import FastMCP
from dotenv import load_dotenv

# Import utilities
from utils.logging_config import setup_logging, get_correlation_id, set_correlation_id
from utils.error_handling import handle_azure_error

# Import tools
from tools.anomaly_detector import get_enterprise_anomalies
from tools.csp_auditor import csp_tenant_audit
from tools.budget_validator import validate_deployment_budget
from tools.governance_advisor import governance_remediation_advisor
from tools.executive_summary import generate_executive_summary
from tools.compliance_overlay import apply_compliance_overlay

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(level=log_level)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Azure FinOps Elite")


@mcp.tool()
def detect_anomalies(
    subscription_ids: Optional[List[str]] = None, threshold: float = 1.5
) -> Dict[str, Any]:
    """
    Detect daily spend spikes across multiple Azure subscriptions.
    
    Compares actual costs vs. historical 7-day averages to identify anomalies.
    Useful for proactive cost monitoring and alerting.
    
    Args:
        subscription_ids: List of subscription IDs to analyze (None = all configured)
        threshold: Anomaly threshold multiplier (default: 1.5 = 50% increase)
    
    Returns:
        Dictionary with anomalies, total count, and excess spend
    
    Example:
        ```python
        result = detect_anomalies(threshold=1.5)
        print(f"Found {result['total_anomalies']} anomalies")
        print(f"Excess spend: ${result['total_excess_spend']}")
        ```
    """
    correlation_id = get_correlation_id()
    set_correlation_id(correlation_id)
    logger.info(f"[{correlation_id}] Starting anomaly detection")

    try:
        result = get_enterprise_anomalies(subscription_ids, threshold)
        logger.info(f"[{correlation_id}] Anomaly detection completed successfully")
        return result
    except Exception as e:
        logger.error(f"[{correlation_id}] Anomaly detection failed: {e}")
        return {"error": handle_azure_error(e)}


@mcp.tool()
def audit_csp_tenants(tenant_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Audit CSP delegated tenants for cost optimization opportunities.
    
    Identifies unattached disks and idle public IPs across multiple tenants.
    Calculates potential monthly and annual savings.
    
    Args:
        tenant_ids: List of tenant IDs to audit (None = all configured CSP tenants)
    
    Returns:
        Dictionary with findings and potential savings
    
    Example:
        ```python
        result = audit_csp_tenants()
        print(f"Total savings: ${result['total_monthly_savings']}/month")
        for tenant in result['tenant_results']:
            print(f"Tenant: {tenant['tenant_name']}")
            print(f"  Unattached disks: {len(tenant['findings']['unattached_disks'])}")
            print(f"  Idle IPs: {len(tenant['findings']['idle_public_ips'])}")
        ```
    """
    correlation_id = get_correlation_id()
    set_correlation_id(correlation_id)
    logger.info(f"[{correlation_id}] Starting CSP tenant audit")

    try:
        result = csp_tenant_audit(tenant_ids)
        logger.info(f"[{correlation_id}] CSP tenant audit completed successfully")
        return result
    except Exception as e:
        logger.error(f"[{correlation_id}] CSP tenant audit failed: {e}")
        return {"error": handle_azure_error(e)}


@mcp.tool()
def validate_budget(
    template: Dict[str, Any],
    budget_limit: Optional[float] = None,
    region: str = "eastus",
) -> Dict[str, Any]:
    """
    Validate infrastructure deployment costs before execution.
    
    Parses ARM template or Bicep JSON output and estimates costs using Azure pricing.
    Compares against budget threshold if provided.
    
    Args:
        template: ARM template or Bicep JSON output
        budget_limit: Optional budget limit in USD
        region: Azure region for pricing (default: eastus)
    
    Returns:
        Dictionary with cost estimates and budget validation
    
    Example:
        ```python
        template = {
            "resources": [
                {
                    "type": "Microsoft.Compute/virtualMachines",
                    "name": "vm-app-01",
                    "properties": {
                        "hardwareProfile": {"vmSize": "Standard_D4s_v3"}
                    }
                }
            ]
        }
        result = validate_budget(template, budget_limit=5000.0)
        print(f"Estimated cost: ${result['estimated_monthly_cost']}/month")
        print(f"Within budget: {result['within_budget']}")
        ```
    """
    correlation_id = get_correlation_id()
    set_correlation_id(correlation_id)
    logger.info(f"[{correlation_id}] Starting budget validation")

    try:
        result = validate_deployment_budget(template, budget_limit, region)
        logger.info(f"[{correlation_id}] Budget validation completed successfully")
        return result
    except Exception as e:
        logger.error(f"[{correlation_id}] Budget validation failed: {e}")
        return {"error": handle_azure_error(e)}


@mcp.tool()
def get_governance_recommendations(
    subscription_ids: Optional[List[str]] = None, min_risk_score: int = 5
) -> Dict[str, Any]:
    """
    Get Azure Advisor recommendations with custom risk scoring.
    
    Applies risk scoring based on NIA Qatar and ISO 27001 frameworks.
    Prioritizes recommendations by security, compliance, and cost impact.
    
    Args:
        subscription_ids: List of subscription IDs (None = all configured)
        min_risk_score: Minimum risk score to include (1-10 scale, default: 5)
    
    Returns:
        Dictionary with prioritized recommendations and summary
    
    Example:
        ```python
        result = get_governance_recommendations(min_risk_score=7)
        print(f"High-risk recommendations: {result['summary']['high_risk_count']}")
        for rec in result['recommendations'][:5]:
            print(f"[Risk {rec['risk_score']}] {rec['title']}")
            print(f"  ISO 27001: {rec['risk_factors']['iso_27001_controls']}")
            print(f"  Remediation: {rec['remediation_steps']}")
        ```
    """
    correlation_id = get_correlation_id()
    set_correlation_id(correlation_id)
    logger.info(f"[{correlation_id}] Starting governance recommendations")

    try:
        result = governance_remediation_advisor(subscription_ids, min_risk_score)
        logger.info(f"[{correlation_id}] Governance recommendations completed successfully")
        return result
    except Exception as e:
        logger.error(f"[{correlation_id}] Governance recommendations failed: {e}")
        return {"error": handle_azure_error(e)}


@mcp.tool()
def create_executive_summary(
    subscription_ids: Optional[List[str]] = None,
    period: str = "monthly",
) -> Dict[str, Any]:
    """
    Generate a Markdown-formatted FinOps ROI Report for executives.
    
    Combines data from all FinOps tools into a non-technical summary
    highlighting cost savings, risks, and ROI for stakeholders.
    
    Args:
        subscription_ids: List of subscription IDs to analyze
        period: Reporting period ("monthly" or "annual")
    
    Returns:
        Dictionary with markdown_report and summary metrics
    
    Example:
        ```python
        result = create_executive_summary(period="annual")
        print(result['markdown_report'])
        print(f"Total savings: ${result['summary_metrics']['total_savings_potential']}")
        ```
    """
    correlation_id = get_correlation_id()
    set_correlation_id(correlation_id)
    logger.info(f"[{correlation_id}] Generating executive summary")

    try:
        result = generate_executive_summary(subscription_ids=subscription_ids, period=period)
        logger.info(f"[{correlation_id}] Executive summary generated successfully")
        return result
    except Exception as e:
        logger.error(f"[{correlation_id}] Executive summary generation failed: {e}")
        return {"error": handle_azure_error(e)}


@mcp.tool()
def check_compliance_impact(
    cost_recommendations: List[Dict[str, Any]],
    check_iso27001: bool = True,
    check_nia_qatar: bool = True,
) -> Dict[str, Any]:
    """
    Apply compliance overlay to cost-saving recommendations.
    
    Flags recommendations that may impact ISO 27001 or NIA Qatar compliance.
    Helps ensure cost optimization doesn't compromise security or compliance.
    
    Args:
        cost_recommendations: List of cost-saving recommendations
        check_iso27001: Check ISO 27001 compliance impact
        check_nia_qatar: Check NIA Qatar compliance impact
    
    Returns:
        Dictionary with flagged recommendations and compliance warnings
    
    Example:
        ```python
        recommendations = [
            {
                "title": "Downgrade to Standard storage",
                "description": "Switch from Premium to Standard SSD",
                "resource_type": "Microsoft.Compute/disks"
            }
        ]
        result = check_compliance_impact(recommendations)
        print(f"Flagged: {result['summary']['flagged_count']}")
        print(f"Safe: {result['summary']['safe_count']}")
        for warning in result['compliance_warnings']:
            print(f"⚠️  {warning['recommendation_title']}")
            print(f"   {warning['action_required']}")
        ```
    """
    correlation_id = get_correlation_id()
    set_correlation_id(correlation_id)
    logger.info(f"[{correlation_id}] Applying compliance overlay")

    try:
        result = apply_compliance_overlay(cost_recommendations, check_iso27001, check_nia_qatar)
        logger.info(f"[{correlation_id}] Compliance overlay completed successfully")
        return result
    except Exception as e:
        logger.error(f"[{correlation_id}] Compliance overlay failed: {e}")
        return {"error": handle_azure_error(e)}


if __name__ == "__main__":
    logger.info("Starting Azure FinOps Elite MCP Server")
    logger.info(f"Log level: {log_level}")

    # Verify environment configuration
    required_vars = ["AZURE_TENANT_ID", "AZURE_CLIENT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.warning(
            f"Missing environment variables: {', '.join(missing_vars)}. "
            "Please configure authentication in .env file."
        )

    # Run the MCP server
    mcp.run()
