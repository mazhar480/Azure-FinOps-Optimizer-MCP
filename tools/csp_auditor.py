"""
CSP Tenant Audit Tool.
Audits delegated sub-tenants for unattached disks and idle public IPs.
"""

import logging
import os
from typing import List, Dict, Any
from datetime import datetime

from azure_clients import get_client_factory
from utils.error_handling import retry_with_backoff, handle_azure_error
from utils.pricing import get_disk_monthly_cost, get_public_ip_monthly_cost

logger = logging.getLogger(__name__)


@retry_with_backoff(max_retries=3)
def csp_tenant_audit(tenant_ids: List[str] = None) -> Dict[str, Any]:
    """
    Audit CSP delegated tenants for cost optimization opportunities.
    
    Identifies:
    - Unattached managed disks
    - Idle public IP addresses
    
    Args:
        tenant_ids: List of tenant IDs to audit (None = all configured CSP tenants)
    
    Returns:
        Dictionary with findings and potential savings
    """
    try:
        logger.info("Starting CSP tenant audit")

        # Get tenant IDs from environment if not provided
        if tenant_ids is None:
            tenant_ids_str = os.getenv("CSP_TENANT_IDS", "")
            if tenant_ids_str:
                tenant_ids = [t.strip() for t in tenant_ids_str.split(",") if t.strip()]
            else:
                # If no CSP tenants configured, audit current subscription's tenant
                logger.warning("No CSP_TENANT_IDS configured. Auditing current subscriptions.")
                return _audit_current_subscriptions()

        if not tenant_ids:
            raise ValueError(
                "No tenant IDs provided. Set CSP_TENANT_IDS environment variable "
                "or pass tenant_ids parameter."
            )

        all_results = []
        for tenant_id in tenant_ids:
            logger.info(f"Auditing tenant {tenant_id[:8]}...")
            result = _audit_tenant(tenant_id)
            all_results.append(result)

        # Aggregate results
        total_savings = sum(r["total_monthly_savings"] for r in all_results)
        total_subscriptions = sum(r["subscriptions_audited"] for r in all_results)

        return {
            "tenants_audited": len(all_results),
            "total_subscriptions_audited": total_subscriptions,
            "total_monthly_savings": round(total_savings, 2),
            "total_annual_savings": round(total_savings * 12, 2),
            "tenant_results": all_results,
            "audit_date": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"CSP tenant audit failed: {e}")
        return {"error": handle_azure_error(e)}


def _audit_current_subscriptions() -> Dict[str, Any]:
    """
    Audit current subscriptions (non-CSP mode).
    
    Returns:
        Audit results for configured subscriptions
    """
    client_factory = get_client_factory()
    subscription_ids = client_factory.get_subscription_ids()

    if not subscription_ids:
        raise ValueError("No subscriptions configured. Set AZURE_SUBSCRIPTION_IDS.")

    unattached_disks = []
    idle_public_ips = []

    for sub_id in subscription_ids:
        logger.info(f"Auditing subscription {sub_id[:8]}...")
        disks = _find_unattached_disks(sub_id)
        ips = _find_idle_public_ips(sub_id)
        unattached_disks.extend(disks)
        idle_public_ips.extend(ips)

    # Calculate savings
    total_savings = 0.0
    for disk in unattached_disks:
        total_savings += disk.get("monthly_cost", 0.0)
    for ip in idle_public_ips:
        total_savings += ip.get("monthly_cost", 0.0)

    return {
        "tenant_id": "current",
        "tenant_name": "Current Tenant",
        "subscriptions_audited": len(subscription_ids),
        "findings": {
            "unattached_disks": unattached_disks,
            "idle_public_ips": idle_public_ips,
        },
        "total_monthly_savings": round(total_savings, 2),
    }


def _audit_tenant(tenant_id: str) -> Dict[str, Any]:
    """
    Audit a single CSP tenant.
    
    Args:
        tenant_id: Azure tenant ID
    
    Returns:
        Audit results for the tenant
    """
    # Note: In production, you would authenticate with CSP credentials
    # and enumerate delegated subscriptions for this tenant
    # For now, we'll use the current subscriptions as a placeholder

    logger.warning(
        f"CSP multi-tenant support requires Azure Lighthouse delegation. "
        f"Auditing current subscriptions for tenant {tenant_id[:8]}..."
    )

    return _audit_current_subscriptions()


def _find_unattached_disks(subscription_id: str) -> List[Dict]:
    """
    Find unattached managed disks in a subscription.
    
    Args:
        subscription_id: Azure subscription ID
    
    Returns:
        List of unattached disk details
    """
    unattached_disks = []

    try:
        client_factory = get_client_factory()
        compute_client = client_factory.get_compute_client(subscription_id)

        # List all managed disks
        for disk in compute_client.disks.list():
            # Check if disk is unattached
            if disk.disk_state == "Unattached":
                # Estimate cost
                monthly_cost = get_disk_monthly_cost(
                    disk.sku.name, disk.disk_size_gb or 128
                ) or 0.0

                unattached_disks.append(
                    {
                        "subscription_id": subscription_id,
                        "resource_group": disk.id.split("/")[4],  # Extract RG from resource ID
                        "disk_name": disk.name,
                        "size_gb": disk.disk_size_gb,
                        "sku": disk.sku.name,
                        "monthly_cost": monthly_cost,
                        "created_date": disk.time_created.strftime("%Y-%m-%d")
                        if disk.time_created
                        else "Unknown",
                        "location": disk.location,
                    }
                )

        logger.info(
            f"Found {len(unattached_disks)} unattached disks in subscription {subscription_id[:8]}"
        )

    except Exception as e:
        logger.error(f"Failed to find unattached disks in {subscription_id[:8]}: {e}")

    return unattached_disks


def _find_idle_public_ips(subscription_id: str) -> List[Dict]:
    """
    Find idle public IP addresses in a subscription.
    
    Args:
        subscription_id: Azure subscription ID
    
    Returns:
        List of idle public IP details
    """
    idle_ips = []

    try:
        client_factory = get_client_factory()
        network_client = client_factory.get_network_client(subscription_id)

        # List all public IP addresses
        for ip in network_client.public_ip_addresses.list_all():
            # Check if IP is not associated with any resource
            if not ip.ip_configuration:
                # Estimate cost
                monthly_cost = get_public_ip_monthly_cost(ip.sku.name or "Standard")

                idle_ips.append(
                    {
                        "subscription_id": subscription_id,
                        "resource_group": ip.id.split("/")[4],  # Extract RG from resource ID
                        "ip_name": ip.name,
                        "ip_address": ip.ip_address or "Not allocated",
                        "sku": ip.sku.name or "Standard",
                        "monthly_cost": monthly_cost,
                        "created_date": "Unknown",  # Public IP doesn't expose creation date
                        "location": ip.location,
                    }
                )

        logger.info(
            f"Found {len(idle_ips)} idle public IPs in subscription {subscription_id[:8]}"
        )

    except Exception as e:
        logger.error(f"Failed to find idle public IPs in {subscription_id[:8]}: {e}")

    return idle_ips
