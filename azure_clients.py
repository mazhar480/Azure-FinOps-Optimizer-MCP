"""
Azure SDK client factory for FinOps Elite MCP Server.
Provides singleton clients for Cost Management, Consumption, Resource, and Advisor APIs.
"""

import os
import logging
from typing import Dict, List, Optional
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.advisor import AdvisorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.core.credentials import TokenCredential

from auth import get_credential

logger = logging.getLogger(__name__)


class AzureClientFactory:
    """
    Factory for creating and caching Azure SDK clients.
    Implements singleton pattern for client reuse across requests.
    """

    def __init__(self, credential: Optional[TokenCredential] = None):
        self.credential = credential or get_credential()
        self._clients: Dict[str, any] = {}
        self._subscription_ids: List[str] = []
        self._load_subscription_ids()

    def _load_subscription_ids(self) -> None:
        """Load subscription IDs from environment variable."""
        sub_ids = os.getenv("AZURE_SUBSCRIPTION_IDS", "")
        if sub_ids:
            self._subscription_ids = [s.strip() for s in sub_ids.split(",") if s.strip()]
            logger.info(f"Loaded {len(self._subscription_ids)} subscription IDs")
        else:
            logger.warning(
                "No subscription IDs configured. Set AZURE_SUBSCRIPTION_IDS environment variable."
            )

    def get_subscription_ids(self) -> List[str]:
        """
        Get configured subscription IDs.
        
        Returns:
            List of subscription IDs
        """
        return self._subscription_ids

    def get_cost_management_client(self) -> CostManagementClient:
        """
        Get Cost Management client for cost analysis and budgets.
        
        Returns:
            CostManagementClient instance
        """
        if "cost_management" not in self._clients:
            self._clients["cost_management"] = CostManagementClient(
                credential=self.credential
            )
            logger.debug("Created Cost Management client")
        return self._clients["cost_management"]

    def get_consumption_client(self, subscription_id: str) -> ConsumptionManagementClient:
        """
        Get Consumption client for usage details and price sheets.
        
        Args:
            subscription_id: Azure subscription ID
        
        Returns:
            ConsumptionManagementClient instance
        """
        key = f"consumption_{subscription_id}"
        if key not in self._clients:
            self._clients[key] = ConsumptionManagementClient(
                credential=self.credential, subscription_id=subscription_id
            )
            logger.debug(f"Created Consumption client for subscription {subscription_id[:8]}...")
        return self._clients[key]

    def get_resource_client(self, subscription_id: str) -> ResourceManagementClient:
        """
        Get Resource Management client for resource metadata.
        
        Args:
            subscription_id: Azure subscription ID
        
        Returns:
            ResourceManagementClient instance
        """
        key = f"resource_{subscription_id}"
        if key not in self._clients:
            self._clients[key] = ResourceManagementClient(
                credential=self.credential, subscription_id=subscription_id
            )
            logger.debug(f"Created Resource client for subscription {subscription_id[:8]}...")
        return self._clients[key]

    def get_subscription_client(self) -> SubscriptionClient:
        """
        Get Subscription client for listing subscriptions.
        
        Returns:
            SubscriptionClient instance
        """
        if "subscription" not in self._clients:
            self._clients["subscription"] = SubscriptionClient(credential=self.credential)
            logger.debug("Created Subscription client")
        return self._clients["subscription"]

    def get_advisor_client(self, subscription_id: str) -> AdvisorManagementClient:
        """
        Get Advisor client for recommendations.
        
        Args:
            subscription_id: Azure subscription ID
        
        Returns:
            AdvisorManagementClient instance
        """
        key = f"advisor_{subscription_id}"
        if key not in self._clients:
            self._clients[key] = AdvisorManagementClient(
                credential=self.credential, subscription_id=subscription_id
            )
            logger.debug(f"Created Advisor client for subscription {subscription_id[:8]}...")
        return self._clients[key]

    def get_compute_client(self, subscription_id: str) -> ComputeManagementClient:
        """
        Get Compute client for VM and disk management.
        
        Args:
            subscription_id: Azure subscription ID
        
        Returns:
            ComputeManagementClient instance
        """
        key = f"compute_{subscription_id}"
        if key not in self._clients:
            self._clients[key] = ComputeManagementClient(
                credential=self.credential, subscription_id=subscription_id
            )
            logger.debug(f"Created Compute client for subscription {subscription_id[:8]}...")
        return self._clients[key]

    def get_network_client(self, subscription_id: str) -> NetworkManagementClient:
        """
        Get Network client for public IPs and networking resources.
        
        Args:
            subscription_id: Azure subscription ID
        
        Returns:
            NetworkManagementClient instance
        """
        key = f"network_{subscription_id}"
        if key not in self._clients:
            self._clients[key] = NetworkManagementClient(
                credential=self.credential, subscription_id=subscription_id
            )
            logger.debug(f"Created Network client for subscription {subscription_id[:8]}...")
        return self._clients[key]

    def list_subscriptions(self) -> List[Dict[str, str]]:
        """
        List all accessible Azure subscriptions.
        
        Returns:
            List of subscription dictionaries with id, name, and state
        """
        try:
            client = self.get_subscription_client()
            subscriptions = []
            for sub in client.subscriptions.list():
                subscriptions.append(
                    {
                        "subscription_id": sub.subscription_id,
                        "display_name": sub.display_name,
                        "state": sub.state,
                    }
                )
            logger.info(f"Found {len(subscriptions)} accessible subscriptions")
            return subscriptions
        except Exception as e:
            logger.error(f"Failed to list subscriptions: {e}")
            raise


# Singleton instance
_client_factory: Optional[AzureClientFactory] = None


def get_client_factory() -> AzureClientFactory:
    """
    Get or create the singleton AzureClientFactory instance.
    
    Returns:
        AzureClientFactory instance
    """
    global _client_factory
    if _client_factory is None:
        _client_factory = AzureClientFactory()
    return _client_factory
