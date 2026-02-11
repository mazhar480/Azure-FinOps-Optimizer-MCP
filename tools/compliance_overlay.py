"""
Compliance Overlay Logic Layer.
Flags if cost-saving recommendations impact ISO 27001 or NIA Qatar controls.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# ISO 27001 controls that may be impacted by cost optimization
ISO_27001_COST_CONTROLS = {
    "encryption": {
        "controls": ["A.8.2.3", "A.10.1.1", "A.10.1.2"],
        "description": "Encryption of information",
        "cost_impact": "Premium storage SKUs required for encryption",
    },
    "backup": {
        "controls": ["A.12.3.1"],
        "description": "Information backup",
        "cost_impact": "Backup storage and retention costs",
    },
    "monitoring": {
        "controls": ["A.12.4.1", "A.12.4.2"],
        "description": "Event logging and monitoring",
        "cost_impact": "Log Analytics and monitoring costs",
    },
    "availability": {
        "controls": ["A.17.1.1", "A.17.2.1"],
        "description": "Availability of information processing facilities",
        "cost_impact": "Redundancy and high-availability configurations",
    },
}

# NIA Qatar requirements that may be impacted by cost optimization
NIA_QATAR_COST_REQUIREMENTS = {
    "data_sovereignty": {
        "requirement": "Data must be stored in Qatar or approved regions",
        "cost_impact": "Qatar region may have higher costs than other regions",
    },
    "encryption_at_rest": {
        "requirement": "All data must be encrypted at rest",
        "cost_impact": "Premium storage SKUs required",
    },
    "high_availability": {
        "requirement": "Critical systems must have 99.9% uptime",
        "cost_impact": "Zone-redundant and geo-redundant configurations",
    },
    "audit_logging": {
        "requirement": "All access must be logged for 90+ days",
        "cost_impact": "Log retention and storage costs",
    },
}


def apply_compliance_overlay(
    cost_recommendations: List[Dict[str, Any]],
    check_iso27001: bool = True,
    check_nia_qatar: bool = True,
) -> Dict[str, Any]:
    """
    Apply compliance overlay to cost-saving recommendations.
    
    Flags recommendations that may impact ISO 27001 or NIA Qatar compliance.
    
    Args:
        cost_recommendations: List of cost-saving recommendations
        check_iso27001: Check ISO 27001 compliance impact
        check_nia_qatar: Check NIA Qatar compliance impact
    
    Returns:
        Dictionary with flagged recommendations and compliance warnings
    """
    logger.info("Applying compliance overlay to cost recommendations")
    
    flagged_recommendations = []
    compliance_warnings = []
    safe_recommendations = []
    
    for rec in cost_recommendations:
        flags = _check_compliance_impact(rec, check_iso27001, check_nia_qatar)
        
        if flags:
            # Add compliance flags to recommendation
            rec_with_flags = rec.copy()
            rec_with_flags['compliance_flags'] = flags
            rec_with_flags['requires_compliance_review'] = True
            flagged_recommendations.append(rec_with_flags)
            
            # Generate warning
            warning = _generate_compliance_warning(rec, flags)
            compliance_warnings.append(warning)
        else:
            # Safe to implement without compliance review
            rec_safe = rec.copy()
            rec_safe['requires_compliance_review'] = False
            safe_recommendations.append(rec_safe)
    
    result = {
        "flagged_recommendations": flagged_recommendations,
        "safe_recommendations": safe_recommendations,
        "compliance_warnings": compliance_warnings,
        "summary": {
            "total_recommendations": len(cost_recommendations),
            "flagged_count": len(flagged_recommendations),
            "safe_count": len(safe_recommendations),
        },
    }
    
    logger.info(
        f"Compliance overlay complete: {len(flagged_recommendations)} flagged, "
        f"{len(safe_recommendations)} safe"
    )
    
    return result


def _check_compliance_impact(
    recommendation: Dict[str, Any],
    check_iso27001: bool,
    check_nia_qatar: bool,
) -> List[Dict[str, Any]]:
    """
    Check if a recommendation impacts compliance controls.
    
    Args:
        recommendation: Cost-saving recommendation
        check_iso27001: Check ISO 27001 impact
        check_nia_qatar: Check NIA Qatar impact
    
    Returns:
        List of compliance flags
    """
    flags = []
    
    rec_text = (
        recommendation.get('title', '') + ' ' +
        recommendation.get('description', '') + ' ' +
        recommendation.get('resource_type', '')
    ).lower()
    
    # Check ISO 27001 impact
    if check_iso27001:
        # Encryption-related
        if any(keyword in rec_text for keyword in ['encrypt', 'storage', 'disk', 'premium']):
            flags.append({
                "framework": "ISO 27001",
                "controls": ISO_27001_COST_CONTROLS['encryption']['controls'],
                "impact": ISO_27001_COST_CONTROLS['encryption']['description'],
                "warning": ISO_27001_COST_CONTROLS['encryption']['cost_impact'],
                "severity": "high",
            })
        
        # Backup-related
        if any(keyword in rec_text for keyword in ['backup', 'snapshot', 'retention']):
            flags.append({
                "framework": "ISO 27001",
                "controls": ISO_27001_COST_CONTROLS['backup']['controls'],
                "impact": ISO_27001_COST_CONTROLS['backup']['description'],
                "warning": ISO_27001_COST_CONTROLS['backup']['cost_impact'],
                "severity": "high",
            })
        
        # Monitoring-related
        if any(keyword in rec_text for keyword in ['monitor', 'log', 'analytics', 'diagnostic']):
            flags.append({
                "framework": "ISO 27001",
                "controls": ISO_27001_COST_CONTROLS['monitoring']['controls'],
                "impact": ISO_27001_COST_CONTROLS['monitoring']['description'],
                "warning": ISO_27001_COST_CONTROLS['monitoring']['cost_impact'],
                "severity": "medium",
            })
        
        # Availability-related
        if any(keyword in rec_text for keyword in ['redundan', 'availability', 'zone', 'geo']):
            flags.append({
                "framework": "ISO 27001",
                "controls": ISO_27001_COST_CONTROLS['availability']['controls'],
                "impact": ISO_27001_COST_CONTROLS['availability']['description'],
                "warning": ISO_27001_COST_CONTROLS['availability']['cost_impact'],
                "severity": "high",
            })
    
    # Check NIA Qatar impact
    if check_nia_qatar:
        # Data sovereignty
        if any(keyword in rec_text for keyword in ['region', 'location', 'geo']):
            flags.append({
                "framework": "NIA Qatar",
                "requirement": NIA_QATAR_COST_REQUIREMENTS['data_sovereignty']['requirement'],
                "warning": NIA_QATAR_COST_REQUIREMENTS['data_sovereignty']['cost_impact'],
                "severity": "critical",
            })
        
        # Encryption at rest
        if any(keyword in rec_text for keyword in ['encrypt', 'storage', 'disk']):
            flags.append({
                "framework": "NIA Qatar",
                "requirement": NIA_QATAR_COST_REQUIREMENTS['encryption_at_rest']['requirement'],
                "warning": NIA_QATAR_COST_REQUIREMENTS['encryption_at_rest']['cost_impact'],
                "severity": "critical",
            })
        
        # High availability
        if any(keyword in rec_text for keyword in ['availability', 'redundan', 'uptime']):
            flags.append({
                "framework": "NIA Qatar",
                "requirement": NIA_QATAR_COST_REQUIREMENTS['high_availability']['requirement'],
                "warning": NIA_QATAR_COST_REQUIREMENTS['high_availability']['cost_impact'],
                "severity": "high",
            })
        
        # Audit logging
        if any(keyword in rec_text for keyword in ['log', 'audit', 'retention']):
            flags.append({
                "framework": "NIA Qatar",
                "requirement": NIA_QATAR_COST_REQUIREMENTS['audit_logging']['requirement'],
                "warning": NIA_QATAR_COST_REQUIREMENTS['audit_logging']['cost_impact'],
                "severity": "medium",
            })
    
    return flags


def _generate_compliance_warning(
    recommendation: Dict[str, Any],
    flags: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate a compliance warning for a flagged recommendation.
    
    Args:
        recommendation: Cost-saving recommendation
        flags: Compliance flags
    
    Returns:
        Compliance warning dictionary
    """
    # Determine highest severity
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    max_severity = max([severity_order.get(f.get('severity', 'low'), 1) for f in flags])
    severity = [k for k, v in severity_order.items() if v == max_severity][0]
    
    # Build warning message
    frameworks = list(set([f['framework'] for f in flags]))
    
    warning = {
        "recommendation_id": recommendation.get('id', 'unknown'),
        "recommendation_title": recommendation.get('title', 'Unknown'),
        "severity": severity,
        "frameworks_impacted": frameworks,
        "flags": flags,
        "action_required": _get_action_required(severity),
    }
    
    return warning


def _get_action_required(severity: str) -> str:
    """
    Get required action based on severity.
    
    Args:
        severity: Severity level
    
    Returns:
        Action required description
    """
    actions = {
        "critical": "STOP: Do not implement without compliance officer approval. "
                   "May violate regulatory requirements.",
        "high": "REVIEW: Requires security/compliance team review before implementation. "
               "May impact critical controls.",
        "medium": "ASSESS: Review impact on compliance controls. "
                 "Document justification if proceeding.",
        "low": "MONITOR: Minimal compliance impact. Proceed with standard change management.",
    }
    
    return actions.get(severity, actions['medium'])
