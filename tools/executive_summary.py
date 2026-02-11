"""
Executive Summary Generator Tool.
Creates Markdown-formatted FinOps ROI reports for non-technical stakeholders.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from tools.anomaly_detector import get_enterprise_anomalies
from tools.csp_auditor import csp_tenant_audit
from tools.governance_advisor import governance_remediation_advisor
from utils.error_handling import handle_azure_error

logger = logging.getLogger(__name__)


def generate_executive_summary(
    subscription_ids: Optional[List[str]] = None,
    include_anomalies: bool = True,
    include_csp_audit: bool = True,
    include_governance: bool = True,
    period: str = "monthly",
) -> Dict[str, Any]:
    """
    Generate a Markdown-formatted FinOps ROI Report for executives.
    
    Combines data from all FinOps tools into a non-technical summary
    highlighting cost savings, risks, and ROI.
    
    Args:
        subscription_ids: List of subscription IDs to analyze
        include_anomalies: Include anomaly detection results
        include_csp_audit: Include CSP tenant audit results
        include_governance: Include governance recommendations
        period: Reporting period ("monthly" or "annual")
    
    Returns:
        Dictionary with markdown_report and summary metrics
    """
    try:
        logger.info("Generating executive summary report")
        
        # Collect data from all tools
        data = {}
        
        if include_anomalies:
            logger.info("Fetching anomaly data...")
            data['anomalies'] = get_enterprise_anomalies(subscription_ids, threshold=1.5)
        
        if include_csp_audit:
            logger.info("Fetching CSP audit data...")
            data['csp_audit'] = csp_tenant_audit()
        
        if include_governance:
            logger.info("Fetching governance recommendations...")
            data['governance'] = governance_remediation_advisor(subscription_ids, min_risk_score=5)
        
        # Generate markdown report
        markdown_report = _generate_markdown_report(data, period)
        
        # Calculate summary metrics
        summary_metrics = _calculate_summary_metrics(data, period)
        
        result = {
            "markdown_report": markdown_report,
            "summary_metrics": summary_metrics,
            "generated_at": datetime.utcnow().isoformat(),
            "period": period,
        }
        
        logger.info("Executive summary generated successfully")
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate executive summary: {e}")
        return {"error": handle_azure_error(e)}


def _generate_markdown_report(data: Dict[str, Any], period: str) -> str:
    """
    Generate Markdown-formatted executive report.
    
    Args:
        data: Combined data from all tools
        period: Reporting period
    
    Returns:
        Markdown-formatted report
    """
    report_date = datetime.utcnow().strftime("%B %d, %Y")
    multiplier = 12 if period == "annual" else 1
    
    # Header
    markdown = f"""# FinOps ROI Report
**Generated:** {report_date}  
**Reporting Period:** {period.capitalize()}

---

## Executive Summary

This report provides a comprehensive overview of your Azure cloud financial operations, 
highlighting cost optimization opportunities, security risks, and potential ROI.

"""
    
    # Key Metrics Section
    markdown += "## 📊 Key Metrics\n\n"
    
    total_savings = 0.0
    
    # Anomaly metrics
    if 'anomalies' in data and 'error' not in data['anomalies']:
        anomalies = data['anomalies']
        excess_spend = anomalies.get('total_excess_spend', 0)
        total_savings += excess_spend
        
        markdown += f"### Cost Anomalies Detected\n"
        markdown += f"- **Anomalies Found:** {anomalies.get('total_anomalies', 0)}\n"
        markdown += f"- **Excess Spend:** ${excess_spend:,.2f}\n"
        markdown += f"- **Potential {period.capitalize()} Impact:** ${excess_spend * multiplier:,.2f}\n\n"
    
    # CSP Audit metrics
    if 'csp_audit' in data and 'error' not in data['csp_audit']:
        audit = data['csp_audit']
        monthly_savings = audit.get('total_monthly_savings', 0)
        total_savings += monthly_savings
        
        markdown += f"### Wasteful Resources Identified\n"
        markdown += f"- **Monthly Savings Potential:** ${monthly_savings:,.2f}\n"
        markdown += f"- **Annual Savings Potential:** ${monthly_savings * 12:,.2f}\n"
        
        # Count resources
        if audit.get('tenant_results'):
            findings = audit['tenant_results'][0].get('findings', {})
            disk_count = len(findings.get('unattached_disks', []))
            ip_count = len(findings.get('idle_public_ips', []))
            markdown += f"- **Unattached Disks:** {disk_count}\n"
            markdown += f"- **Idle Public IPs:** {ip_count}\n\n"
    
    # Governance metrics
    if 'governance' in data and 'error' not in data['governance']:
        gov = data['governance']
        summary = gov.get('summary', {})
        gov_savings = summary.get('potential_monthly_savings', 0)
        total_savings += gov_savings
        
        markdown += f"### Security & Compliance Risks\n"
        markdown += f"- **High-Risk Items:** {summary.get('high_risk_count', 0)}\n"
        markdown += f"- **Medium-Risk Items:** {summary.get('medium_risk_count', 0)}\n"
        markdown += f"- **Compliance Savings:** ${gov_savings:,.2f}/month\n\n"
    
    # Total ROI
    markdown += f"### 💰 Total ROI Opportunity\n"
    markdown += f"- **{period.capitalize()} Savings:** ${total_savings * multiplier:,.2f}\n"
    markdown += f"- **3-Year Projection:** ${total_savings * 36:,.2f}\n\n"
    
    markdown += "---\n\n"
    
    # Detailed Findings
    markdown += "## 🔍 Detailed Findings\n\n"
    
    # Top Anomalies
    if 'anomalies' in data and 'error' not in data['anomalies']:
        anomalies = data['anomalies'].get('anomalies', [])
        if anomalies:
            markdown += "### Top Cost Anomalies\n\n"
            markdown += "| Service | Resource Group | Actual Cost | Variance |\n"
            markdown += "|---------|----------------|-------------|----------|\n"
            
            for anomaly in anomalies[:5]:
                markdown += f"| {anomaly['service_name']} | "
                markdown += f"{anomaly['resource_group']} | "
                markdown += f"${anomaly['actual_cost']:,.2f} | "
                markdown += f"+{anomaly['variance_percent']:.1f}% |\n"
            
            markdown += "\n**Recommendation:** Investigate these services for unexpected scaling or configuration changes.\n\n"
    
    # Top Wasteful Resources
    if 'csp_audit' in data and 'error' not in data['csp_audit']:
        audit = data['csp_audit']
        if audit.get('tenant_results'):
            findings = audit['tenant_results'][0].get('findings', {})
            disks = findings.get('unattached_disks', [])
            
            if disks:
                markdown += "### Top Wasteful Resources\n\n"
                markdown += "| Resource | Type | Size | Monthly Cost |\n"
                markdown += "|----------|------|------|-------------|\n"
                
                # Sort by cost
                sorted_disks = sorted(disks, key=lambda x: x.get('monthly_cost', 0), reverse=True)
                
                for disk in sorted_disks[:5]:
                    markdown += f"| {disk['disk_name']} | "
                    markdown += f"{disk['sku']} | "
                    markdown += f"{disk['size_gb']}GB | "
                    markdown += f"${disk['monthly_cost']:,.2f} |\n"
                
                markdown += "\n**Recommendation:** Delete or archive these unattached resources to realize immediate savings.\n\n"
    
    # Top Security Risks
    if 'governance' in data and 'error' not in data['governance']:
        recommendations = data['governance'].get('recommendations', [])
        if recommendations:
            markdown += "### Top Security & Compliance Risks\n\n"
            markdown += "| Risk | Category | Impact | Effort |\n"
            markdown += "|------|----------|--------|--------|\n"
            
            for rec in recommendations[:5]:
                markdown += f"| {rec['title'][:50]}... | "
                markdown += f"{rec['category']} | "
                markdown += f"Risk {rec['risk_score']}/10 | "
                markdown += f"{rec['estimated_effort_hours']}h |\n"
            
            markdown += "\n**Recommendation:** Prioritize high-risk items to maintain compliance and security posture.\n\n"
    
    # Action Items
    markdown += "---\n\n"
    markdown += "## ✅ Recommended Actions\n\n"
    markdown += "1. **Immediate (This Week)**\n"
    markdown += "   - Review and delete unattached disks and idle public IPs\n"
    markdown += "   - Investigate top cost anomalies\n"
    markdown += "   - Address critical security risks (Risk Score 9-10)\n\n"
    
    markdown += "2. **Short-term (This Month)**\n"
    markdown += "   - Implement budget alerts for anomaly-prone services\n"
    markdown += "   - Remediate high-risk compliance items (Risk Score 7-8)\n"
    markdown += "   - Establish monthly FinOps review cadence\n\n"
    
    markdown += "3. **Long-term (This Quarter)**\n"
    markdown += "   - Optimize resource sizing based on usage patterns\n"
    markdown += "   - Implement automated cleanup policies\n"
    markdown += "   - Achieve full ISO 27001 and NIA Qatar compliance\n\n"
    
    # Footer
    markdown += "---\n\n"
    markdown += "*This report was generated automatically by Azure FinOps Elite. "
    markdown += "For detailed technical analysis, please consult with your FinOps team.*\n"
    
    return markdown


def _calculate_summary_metrics(data: Dict[str, Any], period: str) -> Dict[str, Any]:
    """
    Calculate summary metrics from collected data.
    
    Args:
        data: Combined data from all tools
        period: Reporting period
    
    Returns:
        Summary metrics dictionary
    """
    multiplier = 12 if period == "annual" else 1
    
    metrics = {
        "total_savings_potential": 0.0,
        "anomaly_count": 0,
        "wasteful_resources_count": 0,
        "high_risk_items": 0,
        "medium_risk_items": 0,
    }
    
    # Anomaly metrics
    if 'anomalies' in data and 'error' not in data['anomalies']:
        anomalies = data['anomalies']
        metrics['anomaly_count'] = anomalies.get('total_anomalies', 0)
        metrics['total_savings_potential'] += anomalies.get('total_excess_spend', 0) * multiplier
    
    # CSP audit metrics
    if 'csp_audit' in data and 'error' not in data['csp_audit']:
        audit = data['csp_audit']
        metrics['total_savings_potential'] += audit.get('total_monthly_savings', 0) * multiplier
        
        if audit.get('tenant_results'):
            findings = audit['tenant_results'][0].get('findings', {})
            metrics['wasteful_resources_count'] = (
                len(findings.get('unattached_disks', [])) +
                len(findings.get('idle_public_ips', []))
            )
    
    # Governance metrics
    if 'governance' in data and 'error' not in data['governance']:
        gov = data['governance']
        summary = gov.get('summary', {})
        metrics['high_risk_items'] = summary.get('high_risk_count', 0)
        metrics['medium_risk_items'] = summary.get('medium_risk_count', 0)
        metrics['total_savings_potential'] += summary.get('potential_monthly_savings', 0) * multiplier
    
    # Round total savings
    metrics['total_savings_potential'] = round(metrics['total_savings_potential'], 2)
    
    return metrics
