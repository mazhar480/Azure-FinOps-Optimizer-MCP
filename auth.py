"""
Authentication module for Azure FinOps Elite MCP Server.
Supports Service Principal with Certificate and Managed Identity authentication.
"""

import os
import logging
from typing import Optional
from azure.identity import (
    CertificateCredential,
    ManagedIdentityCredential,
    DefaultAzureCredential,
)
from azure.core.credentials import TokenCredential
from azure.core.exceptions import ClientAuthenticationError

logger = logging.getLogger(__name__)


class AzureAuthenticator:
    """
    Handles Azure authentication with support for:
    - Service Principal with Certificate (production)
    - Managed Identity (Azure-hosted deployments)
    - Default Azure Credential (development fallback)
    """

    def __init__(self):
        self.credential: Optional[TokenCredential] = None
        self.tenant_id: Optional[str] = None
        self.client_id: Optional[str] = None
        self._initialize_credential()

    def _initialize_credential(self) -> None:
        """
        Initialize Azure credential based on environment configuration.
        Priority: Certificate > Managed Identity > Default Credential
        """
        use_managed_identity = os.getenv("USE_MANAGED_IDENTITY", "false").lower() == "true"

        if use_managed_identity:
            logger.info("Using Managed Identity authentication")
            self.credential = self._get_managed_identity_credential()
        else:
            logger.info("Using Service Principal with Certificate authentication")
            self.credential = self._get_certificate_credential()

        # Validate credential by attempting to get a token
        self._validate_credential()

    def _get_certificate_credential(self) -> TokenCredential:
        """
        Create certificate-based credential for Service Principal.
        Requires: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CERTIFICATE_PATH
        """
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        cert_path = os.getenv("AZURE_CERTIFICATE_PATH")
        cert_password = os.getenv("AZURE_CERTIFICATE_PASSWORD")

        if not all([self.tenant_id, self.client_id, cert_path]):
            logger.warning(
                "Certificate authentication not fully configured. "
                "Falling back to DefaultAzureCredential."
            )
            return DefaultAzureCredential()

        if not os.path.exists(cert_path):
            raise FileNotFoundError(
                f"Certificate file not found: {cert_path}. "
                "Please ensure AZURE_CERTIFICATE_PATH points to a valid .pem file."
            )

        try:
            credential = CertificateCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                certificate_path=cert_path,
                password=cert_password,
            )
            logger.info(
                f"Certificate credential initialized for tenant: {self.tenant_id[:8]}..."
            )
            return credential
        except Exception as e:
            logger.error(f"Failed to initialize certificate credential: {e}")
            logger.warning("Falling back to DefaultAzureCredential")
            return DefaultAzureCredential()

    def _get_managed_identity_credential(self) -> TokenCredential:
        """
        Create Managed Identity credential for Azure-hosted deployments.
        Works with: Azure VMs, App Service, Container Apps, AKS
        """
        try:
            credential = ManagedIdentityCredential()
            logger.info("Managed Identity credential initialized")
            return credential
        except Exception as e:
            logger.error(f"Failed to initialize Managed Identity: {e}")
            logger.warning("Falling back to DefaultAzureCredential")
            return DefaultAzureCredential()

    def _validate_credential(self) -> None:
        """
        Validate the credential by attempting to acquire a token.
        This ensures authentication is working before making API calls.
        """
        try:
            # Attempt to get a token for Azure Resource Manager
            token = self.credential.get_token("https://management.azure.com/.default")
            logger.info("Credential validation successful")
            logger.debug(f"Token expires at: {token.expires_on}")
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise RuntimeError(
                "Azure authentication failed. Please check your credentials and permissions. "
                "Ensure the Service Principal has the required RBAC roles: "
                "Cost Management Reader, Reader, Advisor Reader."
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error during credential validation: {e}")
            raise

    def get_credential(self) -> TokenCredential:
        """
        Get the initialized Azure credential.
        
        Returns:
            TokenCredential: Azure credential for SDK clients
        """
        if not self.credential:
            raise RuntimeError("Credential not initialized. Call _initialize_credential() first.")
        return self.credential

    def refresh_credential(self) -> None:
        """
        Refresh the credential. Useful for long-running processes.
        """
        logger.info("Refreshing Azure credential")
        self._initialize_credential()


# Singleton instance for application-wide use
_authenticator: Optional[AzureAuthenticator] = None


def get_authenticator() -> AzureAuthenticator:
    """
    Get or create the singleton AzureAuthenticator instance.
    
    Returns:
        AzureAuthenticator: Singleton authenticator instance
    """
    global _authenticator
    if _authenticator is None:
        _authenticator = AzureAuthenticator()
    return _authenticator


def get_credential() -> TokenCredential:
    """
    Convenience function to get the Azure credential directly.
    
    Returns:
        TokenCredential: Azure credential for SDK clients
    """
    return get_authenticator().get_credential()
