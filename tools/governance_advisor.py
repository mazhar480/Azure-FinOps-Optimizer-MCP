"""
Governance Remediation Advisor Tool.
Integrates Azure Advisor with custom risk scoring based on NIA Qatar and ISO 27001.
"""

import logging
from typing import List, Dict, Any, Optional

from azure_clients import get_client_factory
from utils.error_handling import retry_with_backoff, handle_azure_error

logger = logging.getLogger(__name__)


# ISO 27001 control mappings
ISO_27001_CONTROLS = {
    "encryption": ["A.8.2.3", "A.10.1.1"],  # Cryptographic controls
    "access_control": ["A.9.1.1", "A.9.2.1"],  # Access control policy
    "backup": ["A.12.3.1"],  # Information backup
    "monitoring": ["A.12.4.1"],  # Event logging
    "vulnerability": ["A.12.6.1"],  # Technical vulnerability management
    "network_security": ["A.13.1.1"],  # Network controls
    "compliance": ["A.18.1.1"],  # Compliance with legal requirements
}

# NIA Qatar framework requirements
NIA_QATAR_REQUIREMENTS = {
    "data_sovereignty": "Data must be stored in Qatar or approved regions",
    "encryption_at_rest": "All data must be encrypted at rest",
    "encryption_in_transit": "All data must be encrypted in transit",
    "access_logging": "All access must be logged and monitored",
    "multi_factor_auth": "MFA required for all administrative access",
}


@retry_with_backoff(max_retries=3)
def governance_remediation_advisor(
    subscription_ids: List[str] = None, min_risk_score: int = 5
) -> Dict[str, Any]:
    """
    Get Azure Advisor recommendations with custom risk scoring.
    
    Applies risk scoring based on NIA Qatar and ISO 27001 frameworks.
    
    Args:
        subscription_ids: List of subscription IDs (None = all configured)
        min_risk_score: Minimum risk score to include (1-10 scale)
    
    Returns:
        Dictionary with prioritized recommendations and summary
    """
    try:
        logger.info(f"Fetching governance recommendations (min risk score: {min_risk_score})")

        client_factory = get_client_factory()
        if subscription_ids is None:
            subscription_ids = client_factory.get_subscription_ids()

        if not subscription_ids:
            raise ValueError("No subscription IDs provided. Set AZURE_SUBSCRIPTION_IDS.")

        all_recommendations = []

        for sub_id in subscription_ids:
            logger.info(f"Analyzing subscription {sub_id[:8]}...")
            recommendations = _get_advisor_recommendations(sub_id)
            all_recommendations.extend(recommendations)

        # Filter by minimum risk score
        filtered_recommendations = [
            r for r in all_recommendations if r["risk_score"] >= min_risk_score
        ]

        # Sort by risk score (highest first)
        filtered_recommendations.sort(key=lambda x: x["risk_score"], reverse=True)

        # Calculate summary
        summary = _calculate_summary(filtered_recommendations)

        result = {
            "recommendations": filtered_recommendations,
            "summary": summary,
            "min_risk_score": min_risk_score,
        }

        logger.info(
            f"Found {len(filtered_recommendations)} recommendations "
            f"with {summary['high_risk_count']} high-risk items"
        )
        return result

    except Exception as e:
        logger.error(f"Governance advisor failed: {e}")
        return {"error": handle_azure_error(e)}


def _get_advisor_recommendations(subscription_id: str) -> List[Dict]:
    """
    Get Azure Advisor recommendations for a subscription.
    
    Args:
        subscription_id: Azure subscription ID
    
    Returns:
        List of recommendations with risk scores
    """
    recommendations = []

    try:
        client_factory = get_client_factory()
        advisor_client = client_factory.get_advisor_client(subscription_id)

        # Get all recommendations
        for rec in advisor_client.recommendations.list():
            # Calculate custom risk score
            risk_score, risk_factors = _calculate_risk_score(rec)

            # Extract remediation steps
            remediation_steps = _extract_remediation_steps(rec)

            recommendations.append(
                {
                    "id": rec.id,
                    "subscription_id": subscription_id,
                    "category": rec.category,
                    "title": rec.short_description.problem if rec.short_description else "Unknown",
                    "description": rec.short_description.solution
                    if rec.short_description
                    else "No description",
                    "risk_score": risk_score,
                    "risk_factors": risk_factors,
                    "remediation_steps": remediation_steps,
                    "estimated_cost": _extract_cost_impact(rec),
                    "estimated_effort_hours": _estimate_effort(rec),
                    "impacted_resource": rec.impacted_value or "Unknown",
                }
            )

    except Exception as e:
        logger.error(f"Failed to get recommendations for {subscription_id[:8]}: {e}")

    return recommendations


def _calculate_risk_score(recommendation: Any) -> tuple[int, Dict[str, Any]]:
    """
    Calculate custom risk score based on NIA Qatar and ISO 27001.
    
    Args:
        recommendation: Azure Advisor recommendation
    
    Returns:
        Tuple of (risk_score, risk_factors)
    """
    score = 0
    risk_factors = {
        "iso_27001_controls": [],
        "nia_qatar_requirements": [],
        "cost_impact": "Unknown",
        "security_impact": "Unknown",
    }

    category = recommendation.category
    impact = recommendation.impact or "Medium"
    problem = (
        recommendation.short_description.problem.lower()
        if recommendation.short_description
        else ""
    )

    # Security impact scoring
    if category == "Security":
        if impact == "High":
            score += 4
            risk_factors["security_impact"] = "Critical"
        elif impact == "Medium":
            score += 3
            risk_factors["security_impact"] = "High"
        else:
            score += 2
            risk_factors["security_impact"] = "Medium"

        # Check for encryption-related issues
        if "encrypt" in problem:
            risk_factors["iso_27001_controls"].extend(ISO_27001_CONTROLS["encryption"])
            risk_factors["nia_qatar_requirements"].append(
                NIA_QATAR_REQUIREMENTS["encryption_at_rest"]
            )
            score += 2

        # Check for access control issues
        if "access" in problem or "authentication" in problem:
            risk_factors["iso_27001_controls"].extend(ISO_27001_CONTROLS["access_control"])
            risk_factors["nia_qatar_requirements"].append(
                NIA_QATAR_REQUIREMENTS["multi_factor_auth"]
            )
            score += 2

    # Cost impact scoring
    elif category == "Cost":
        # Extract potential savings from metadata
        potential_savings = _extract_cost_impact(recommendation)
        if potential_savings > 1000:
            score += 3
            risk_factors["cost_impact"] = "High"
        elif potential_savings > 100:
            score += 2
            risk_factors["cost_impact"] = "Medium"
        else:
            score += 1
            risk_factors["cost_impact"] = "Low"

    # Performance and Reliability
    elif category in ["Performance", "HighAvailability"]:
        if impact == "High":
            score += 3
        elif impact == "Medium":
            score += 2
        else:
            score += 1

    # Operational Excellence
    elif category == "OperationalExcellence":
        score += 1

    # Production resource bonus
    if "prod" in problem or "production" in problem:
        score += 2

    # Cap score at 10
    score = min(score, 10)

    return score, risk_factors


def _extract_cost_impact(recommendation: Any) -> float:
    """
    Extract cost impact from recommendation metadata.
    
    Args:
        recommendation: Azure Advisor recommendation
    
    Returns:
        Estimated monthly cost impact in USD
    """
    try:
        if recommendation.extended_properties:
            savings = recommendation.extended_properties.get("savingsAmount", "0")
            return float(savings)
    except Exception:
        pass
    return 0.0


def _estimate_effort(recommendation: Any) -> int:
    """
    Estimate remediation effort in hours.
    
    Args:
        recommendation: Azure Advisor recommendation
    
    Returns:
        Estimated hours
    """
    category = recommendation.category
    impact = recommendation.impact or "Medium"

    # Simple heuristic based on category and impact
    effort_map = {
        "Security": {"High": 4, "Medium": 2, "Low": 1},
        "Cost": {"High": 2, "Medium": 1, "Low": 0.5},
        "Performance": {"High": 3, "Medium": 2, "Low": 1},
        "HighAvailability": {"High": 4, "Medium": 3, "Low": 2},
        "OperationalExcellence": {"High": 2, "Medium": 1, "Low": 0.5},
    }

    return effort_map.get(category, {}).get(impact, 2)


def _extract_remediation_steps(recommendation: Any) -> List[str]:
    """
    Extract remediation steps from recommendation.
    
    Args:
        recommendation: Azure Advisor recommendation
    
    Returns:
        List of remediation steps
    """
    steps = []

    if recommendation.short_description and recommendation.short_description.solution:
        # Split solution text into steps
        solution = recommendation.short_description.solution
        steps.append(solution)

    if not steps:
        steps.append("Review Azure Advisor recommendation details in Azure Portal")

    return steps


def _calculate_summary(recommendations: List[Dict]) -> Dict[str, Any]:
    """
    Calculate summary statistics for recommendations.
    
    Args:
        recommendations: List of recommendations
    
    Returns:
        Summary dictionary
    """
    total = len(recommendations)
    high_risk = len([r for r in recommendations if r["risk_score"] >= 7])
    medium_risk = len([r for r in recommendations if 4 <= r["risk_score"] < 7])
    low_risk = len([r for r in recommendations if r["risk_score"] < 4])

    total_savings = sum(r.get("estimated_cost", 0.0) for r in recommendations)

    return {
        "total_recommendations": total,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "potential_monthly_savings": round(total_savings, 2),
        "potential_annual_savings": round(total_savings * 12, 2),
    }
