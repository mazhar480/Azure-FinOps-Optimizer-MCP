"""
Error handling utilities for Azure FinOps Elite MCP Server.
Implements retry logic, rate limiting, and exception handling for Azure APIs.
"""

import logging
import time
from typing import TypeVar, Callable, Any, Optional
from functools import wraps
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ResourceNotFoundError,
    ServiceRequestError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimitExceeded(Exception):
    """Raised when Azure API rate limit is exceeded."""

    pass


class AuthenticationExpired(Exception):
    """Raised when Azure authentication token has expired."""

    pass


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay between retries
    
    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ClientAuthenticationError as e:
                    logger.error(f"Authentication failed: {e}")
                    raise AuthenticationExpired(
                        "Azure authentication token expired. Please refresh credentials."
                    ) from e
                except HttpResponseError as e:
                    last_exception = e

                    # Handle rate limiting (429 Too Many Requests)
                    if e.status_code == 429:
                        retry_after = _get_retry_after(e)
                        if retry_after:
                            wait_time = min(retry_after, max_delay)
                        else:
                            wait_time = min(delay, max_delay)

                        if attempt < max_retries:
                            logger.warning(
                                f"Rate limit exceeded. Retrying in {wait_time}s "
                                f"(attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(wait_time)
                            delay *= backoff_factor
                            continue
                        else:
                            raise RateLimitExceeded(
                                f"Azure API rate limit exceeded after {max_retries} retries. "
                                "Please reduce request frequency."
                            ) from e

                    # Handle transient errors (5xx)
                    elif 500 <= e.status_code < 600:
                        if attempt < max_retries:
                            wait_time = min(delay, max_delay)
                            logger.warning(
                                f"Server error {e.status_code}. Retrying in {wait_time}s "
                                f"(attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(wait_time)
                            delay *= backoff_factor
                            continue
                        else:
                            raise

                    # Don't retry client errors (4xx except 429)
                    else:
                        logger.error(f"Client error {e.status_code}: {e.message}")
                        raise

                except (ServiceRequestError, ConnectionError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = min(delay, max_delay)
                        logger.warning(
                            f"Network error: {e}. Retrying in {wait_time}s "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        delay *= backoff_factor
                        continue
                    else:
                        raise

                except Exception as e:
                    # Don't retry unexpected exceptions
                    logger.error(f"Unexpected error: {e}")
                    raise

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic failed unexpectedly")

        return wrapper

    return decorator


def _get_retry_after(error: HttpResponseError) -> Optional[float]:
    """
    Extract Retry-After header from Azure API error response.
    
    Args:
        error: Azure HTTP response error
    
    Returns:
        Retry delay in seconds, or None if not found
    """
    try:
        if hasattr(error, "response") and error.response:
            retry_after = error.response.headers.get("Retry-After")
            if retry_after:
                # Retry-After can be seconds or HTTP date
                try:
                    return float(retry_after)
                except ValueError:
                    # If it's a date, default to 60 seconds
                    return 60.0
    except Exception as e:
        logger.debug(f"Failed to parse Retry-After header: {e}")
    return None


def handle_azure_error(error: Exception) -> dict:
    """
    Convert Azure SDK exceptions to user-friendly error messages.
    
    Args:
        error: Exception from Azure SDK
    
    Returns:
        Dictionary with error details
    """
    if isinstance(error, ClientAuthenticationError):
        return {
            "error": "Authentication Failed",
            "message": "Azure authentication failed. Please check your credentials and RBAC permissions.",
            "details": str(error),
            "remediation": [
                "Verify AZURE_TENANT_ID, AZURE_CLIENT_ID are correct",
                "Ensure certificate is valid and not expired",
                "Check Service Principal has required RBAC roles: Cost Management Reader, Reader, Advisor Reader",
            ],
        }

    elif isinstance(error, ResourceNotFoundError):
        return {
            "error": "Resource Not Found",
            "message": "The requested Azure resource was not found.",
            "details": str(error),
            "remediation": [
                "Verify subscription ID is correct",
                "Check resource group and resource names",
                "Ensure Service Principal has access to the subscription",
            ],
        }

    elif isinstance(error, RateLimitExceeded):
        return {
            "error": "Rate Limit Exceeded",
            "message": "Azure API rate limit exceeded. Please reduce request frequency.",
            "details": str(error),
            "remediation": [
                "Reduce the number of concurrent requests",
                "Implement caching for frequently accessed data",
                "Consider batching requests",
                "Wait before retrying (recommended: 60 seconds)",
            ],
        }

    elif isinstance(error, HttpResponseError):
        return {
            "error": f"Azure API Error ({error.status_code})",
            "message": error.message or "An error occurred while calling Azure API",
            "details": str(error),
            "remediation": [
                "Check Azure service health status",
                "Verify API permissions and RBAC roles",
                "Review Azure SDK documentation for this error code",
            ],
        }

    else:
        return {
            "error": "Unexpected Error",
            "message": "An unexpected error occurred",
            "details": str(error),
            "remediation": [
                "Check application logs for details",
                "Verify network connectivity to Azure",
                "Contact support if the issue persists",
            ],
        }
