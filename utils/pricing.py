"""
Azure pricing utilities for cost calculations.
Provides helpers for estimating resource costs using Azure Price Sheet API.
"""

import logging
from typing import Dict, Optional, List
from decimal import Decimal

logger = logging.getLogger(__name__)


# Azure pricing data (simplified - in production, query Price Sheet API)
# Prices are monthly estimates in USD for common SKUs
PRICING_DATABASE = {
    # Compute - Virtual Machines (East US, Pay-as-you-go)
    "Microsoft.Compute/virtualMachines": {
        "Standard_B1s": 7.59,
        "Standard_B2s": 30.37,
        "Standard_D2s_v3": 96.36,
        "Standard_D4s_v3": 192.72,
        "Standard_D8s_v3": 385.44,
        "Standard_E2s_v3": 109.50,
        "Standard_E4s_v3": 219.00,
    },
    # Storage - Managed Disks (East US)
    "Microsoft.Compute/disks": {
        "Standard_LRS": {
            "32": 1.54,
            "64": 3.07,
            "128": 6.14,
            "256": 12.29,
            "512": 24.58,
            "1024": 49.15,
        },
        "Premium_LRS": {
            "32": 4.81,
            "64": 9.62,
            "128": 19.71,
            "256": 39.42,
            "512": 78.85,
            "1024": 157.70,
        },
    },
    # Networking - Public IP Addresses
    "Microsoft.Network/publicIPAddresses": {
        "Basic": 3.65,
        "Standard": 3.65,
    },
    # Storage Accounts (per GB)
    "Microsoft.Storage/storageAccounts": {
        "Standard_LRS": 0.0184,  # per GB/month
        "Standard_GRS": 0.0368,
        "Premium_LRS": 0.15,
    },
}


def get_vm_monthly_cost(sku: str, region: str = "eastus") -> Optional[float]:
    """
    Get estimated monthly cost for a VM SKU.
    
    Args:
        sku: VM SKU (e.g., "Standard_D4s_v3")
        region: Azure region (default: eastus)
    
    Returns:
        Monthly cost in USD, or None if SKU not found
    """
    return PRICING_DATABASE.get("Microsoft.Compute/virtualMachines", {}).get(sku)


def get_disk_monthly_cost(sku: str, size_gb: int) -> Optional[float]:
    """
    Get estimated monthly cost for a managed disk.
    
    Args:
        sku: Disk SKU (e.g., "Premium_LRS")
        size_gb: Disk size in GB
    
    Returns:
        Monthly cost in USD, or None if SKU not found
    """
    disk_pricing = PRICING_DATABASE.get("Microsoft.Compute/disks", {}).get(sku, {})
    if not disk_pricing:
        return None

    # Find the closest disk size tier
    available_sizes = sorted([int(s) for s in disk_pricing.keys()])
    selected_size = None
    for size in available_sizes:
        if size >= size_gb:
            selected_size = size
            break

    if selected_size is None:
        selected_size = available_sizes[-1]  # Use largest if exceeds all tiers

    return disk_pricing.get(str(selected_size))


def get_public_ip_monthly_cost(sku: str = "Standard") -> float:
    """
    Get estimated monthly cost for a public IP address.
    
    Args:
        sku: Public IP SKU (Basic or Standard)
    
    Returns:
        Monthly cost in USD
    """
    return PRICING_DATABASE.get("Microsoft.Network/publicIPAddresses", {}).get(sku, 3.65)


def get_storage_account_monthly_cost(sku: str, size_gb: float) -> Optional[float]:
    """
    Get estimated monthly cost for a storage account.
    
    Args:
        sku: Storage SKU (e.g., "Standard_LRS")
        size_gb: Storage size in GB
    
    Returns:
        Monthly cost in USD, or None if SKU not found
    """
    price_per_gb = PRICING_DATABASE.get("Microsoft.Storage/storageAccounts", {}).get(sku)
    if price_per_gb:
        return price_per_gb * size_gb
    return None


def estimate_resource_cost(resource_type: str, sku: str, **kwargs) -> Optional[float]:
    """
    Estimate monthly cost for any Azure resource.
    
    Args:
        resource_type: Azure resource type (e.g., "Microsoft.Compute/virtualMachines")
        sku: Resource SKU
        **kwargs: Additional parameters (size_gb for disks, etc.)
    
    Returns:
        Estimated monthly cost in USD, or None if not found
    """
    if resource_type == "Microsoft.Compute/virtualMachines":
        return get_vm_monthly_cost(sku, kwargs.get("region", "eastus"))
    elif resource_type == "Microsoft.Compute/disks":
        size_gb = kwargs.get("size_gb", 128)
        return get_disk_monthly_cost(sku, size_gb)
    elif resource_type == "Microsoft.Network/publicIPAddresses":
        return get_public_ip_monthly_cost(sku)
    elif resource_type == "Microsoft.Storage/storageAccounts":
        size_gb = kwargs.get("size_gb", 100)
        return get_storage_account_monthly_cost(sku, size_gb)
    else:
        logger.warning(f"No pricing data for resource type: {resource_type}")
        return None


def calculate_savings_potential(resources: List[Dict]) -> Dict[str, float]:
    """
    Calculate potential savings from a list of wasteful resources.
    
    Args:
        resources: List of resource dictionaries with type, sku, and metadata
    
    Returns:
        Dictionary with monthly and annual savings
    """
    monthly_savings = 0.0

    for resource in resources:
        cost = estimate_resource_cost(
            resource.get("resource_type", ""),
            resource.get("sku", ""),
            size_gb=resource.get("size_gb", 128),
            region=resource.get("region", "eastus"),
        )
        if cost:
            monthly_savings += cost

    return {
        "monthly_savings": round(monthly_savings, 2),
        "annual_savings": round(monthly_savings * 12, 2),
    }


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Numeric amount
        currency: Currency code (default: USD)
    
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f} {currency}"
