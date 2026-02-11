"""
Logging configuration for Azure FinOps Elite MCP Server.
Provides structured logging with correlation IDs for enterprise monitoring.
"""

import logging
import sys
import uuid
from typing import Optional
from datetime import datetime


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records for request tracing."""

    def __init__(self):
        super().__init__()
        self.correlation_id: Optional[str] = None

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = self.correlation_id or "N/A"
        return True

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for current context."""
        self.correlation_id = correlation_id

    def clear_correlation_id(self) -> None:
        """Clear correlation ID."""
        self.correlation_id = None


# Global correlation ID filter
_correlation_filter = CorrelationIdFilter()


class StructuredFormatter(logging.Formatter):
    """
    Structured log formatter for enterprise monitoring.
    Outputs JSON-like format for easy parsing by log aggregators.
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        correlation_id = getattr(record, "correlation_id", "N/A")

        log_entry = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": correlation_id,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Format as key=value pairs for readability
        formatted = " ".join([f"{k}={v}" for k, v in log_entry.items()])
        return formatted


def setup_logging(level: str = "INFO") -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(StructuredFormatter())
    console_handler.addFilter(_correlation_filter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # Reduce noise from Azure SDK
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
        logging.WARNING
    )

    logging.info(f"Logging configured at {level} level")


def get_correlation_id() -> str:
    """
    Generate a new correlation ID for request tracing.
    
    Returns:
        str: UUID-based correlation ID
    """
    return str(uuid.uuid4())


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID for current context.
    
    Args:
        correlation_id: Correlation ID to set
    """
    _correlation_filter.set_correlation_id(correlation_id)


def clear_correlation_id() -> None:
    """Clear correlation ID from current context."""
    _correlation_filter.clear_correlation_id()
