"""
Budget Validation Tool.
Validates ARM/Bicep deployment costs against Azure Price Sheet API.
"""

import logging
import json
from typing import Dict, Any, List, Optional

from utils.error_handling import retry_with_backoff, handle_azure_error
from utils.pricing import estimate_resource_cost

logger = logging.getLogger(__name__)


@retry_with_backoff(max_retries=3)
def validate_deployment_budget(
    template: Dict[str, Any],
    budget_limit: Optional[float] = None,
    region: str = "eastus",
) -> Dict[str, Any]:
    """
    Validate infrastructure deployment costs before execution.
    
    Parses ARM/Bicep template and estimates costs using Azure pricing.
    
    Args:
        template: ARM template or Bicep JSON output
        budget_limit: Optional budget limit in USD
        region: Azure region for pricing (default: eastus)
    
    Returns:
        Dictionary with cost estimates and budget validation
    """
    try:
        logger.info(f"Validating deployment budget for region {region}")

        # Parse template resources
        resources = template.get("resources", [])
        if not resources:
            return {
                "error": "No resources found in template",
                "estimated_monthly_cost": 0.0,
                "estimated_annual_cost": 0.0,
            }

        # Estimate costs for each resource
        cost_breakdown = []
        total_monthly_cost = 0.0
        warnings = []

        for resource in resources:
            resource_type = resource.get("type", "")
            resource_name = resource.get("name", "Unknown")

            # Extract SKU and size information
            sku_info = _extract_sku_info(resource)

            if sku_info:
                estimated_cost = estimate_resource_cost(
                    resource_type=resource_type,
                    sku=sku_info["sku"],
                    size_gb=sku_info.get("size_gb", 128),
                    region=region,
                )

                if estimated_cost:
                    cost_breakdown.append(
                        {
                            "resource_type": resource_type,
                            "resource_name": resource_name,
                            "sku": sku_info["sku"],
                            "monthly_cost": round(estimated_cost, 2),
                        }
                    )
                    total_monthly_cost += estimated_cost

                    # Add warnings for expensive resources
                    if "Premium" in sku_info["sku"] and estimated_cost > 50:
                        warnings.append(
                            f"{resource_name}: Premium SKU detected - "
                            f"consider Standard for non-production (${estimated_cost:.2f}/mo)"
                        )
                else:
                    logger.warning(f"No pricing data for {resource_type} with SKU {sku_info['sku']}")
            else:
                logger.debug(f"Could not extract SKU info for {resource_type}")

        # Calculate annual cost
        total_annual_cost = total_monthly_cost * 12

        # Check budget
        within_budget = True
        if budget_limit is not None:
            within_budget = total_monthly_cost <= budget_limit
            if not within_budget:
                warnings.insert(
                    0,
                    f"BUDGET EXCEEDED: Estimated cost ${total_monthly_cost:.2f} "
                    f"exceeds budget ${budget_limit:.2f}",
                )

        result = {
            "estimated_monthly_cost": round(total_monthly_cost, 2),
            "estimated_annual_cost": round(total_annual_cost, 2),
            "budget_limit": budget_limit,
            "within_budget": within_budget,
            "cost_breakdown": cost_breakdown,
            "warnings": warnings,
            "region": region,
            "resources_analyzed": len(resources),
            "resources_priced": len(cost_breakdown),
        }

        logger.info(
            f"Budget validation complete: ${total_monthly_cost:.2f}/mo, "
            f"within budget: {within_budget}"
        )
        return result

    except Exception as e:
        logger.error(f"Budget validation failed: {e}")
        return {"error": handle_azure_error(e)}


def _extract_sku_info(resource: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract SKU and size information from ARM template resource.
    
    Args:
        resource: ARM template resource definition
    
    Returns:
        Dictionary with sku and optional size_gb, or None if not found
    """
    resource_type = resource.get("type", "")
    properties = resource.get("properties", {})
    sku = resource.get("sku", {})

    # Virtual Machines
    if resource_type == "Microsoft.Compute/virtualMachines":
        vm_size = properties.get("hardwareProfile", {}).get("vmSize")
        if vm_size:
            return {"sku": vm_size}

    # Managed Disks
    elif resource_type == "Microsoft.Compute/disks":
        disk_sku = sku.get("name")
        disk_size = properties.get("diskSizeGB", 128)
        if disk_sku:
            return {"sku": disk_sku, "size_gb": disk_size}

    # Public IP Addresses
    elif resource_type == "Microsoft.Network/publicIPAddresses":
        ip_sku = sku.get("name", "Standard")
        return {"sku": ip_sku}

    # Storage Accounts
    elif resource_type == "Microsoft.Storage/storageAccounts":
        storage_sku = sku.get("name")
        if storage_sku:
            # Estimate 100GB for storage accounts (can be parameterized)
            return {"sku": storage_sku, "size_gb": 100}

    return None


def validate_deployment_budget_from_file(
    template_path: str, budget_limit: Optional[float] = None, region: str = "eastus"
) -> Dict[str, Any]:
    """
    Validate deployment budget from ARM template file.
    
    Args:
        template_path: Path to ARM template JSON file
        budget_limit: Optional budget limit in USD
        region: Azure region for pricing
    
    Returns:
        Budget validation results
    """
    try:
        with open(template_path, "r") as f:
            template = json.load(f)
        return validate_deployment_budget(template, budget_limit, region)
    except FileNotFoundError:
        return {"error": f"Template file not found: {template_path}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in template file: {e}"}
