"""
Enterprise Anomaly Detection Tool.
Detects daily spend spikes across multiple Azure subscriptions.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from statistics import mean

from azure.mgmt.costmanagement.models import (
    QueryDefinition,
    QueryDataset,
    QueryAggregation,
    QueryGrouping,
    QueryTimePeriod,
)
from azure_clients import get_client_factory
from utils.error_handling import retry_with_backoff, handle_azure_error

logger = logging.getLogger(__name__)


@retry_with_backoff(max_retries=3)
def get_enterprise_anomalies(
    subscription_ids: List[str] = None, threshold: float = 1.5
) -> Dict[str, Any]:
    """
    Detect daily spend spikes across multiple subscriptions.
    
    Compares actual costs vs. historical 7-day averages to identify anomalies.
    
    Args:
        subscription_ids: List of subscription IDs to analyze (None = all configured)
        threshold: Anomaly threshold multiplier (default: 1.5 = 50% increase)
    
    Returns:
        Dictionary with anomalies, total count, and excess spend
    """
    try:
        logger.info(f"Starting anomaly detection with threshold {threshold}x")

        client_factory = get_client_factory()
        if subscription_ids is None:
            subscription_ids = client_factory.get_subscription_ids()

        if not subscription_ids:
            raise ValueError(
                "No subscription IDs provided. Set AZURE_SUBSCRIPTION_IDS environment variable."
            )

        all_anomalies = []
        total_excess_spend = 0.0

        for sub_id in subscription_ids:
            logger.info(f"Analyzing subscription {sub_id[:8]}...")
            anomalies = _detect_subscription_anomalies(sub_id, threshold)
            all_anomalies.extend(anomalies)

            # Calculate excess spend
            for anomaly in anomalies:
                excess = anomaly["actual_cost"] - anomaly["average_cost"]
                total_excess_spend += excess

        # Sort by variance (highest first)
        all_anomalies.sort(key=lambda x: x["variance_percent"], reverse=True)

        result = {
            "anomalies": all_anomalies,
            "total_anomalies": len(all_anomalies),
            "total_excess_spend": round(total_excess_spend, 2),
            "analysis_date": datetime.utcnow().isoformat(),
            "threshold": threshold,
        }

        logger.info(
            f"Detected {len(all_anomalies)} anomalies with ${total_excess_spend:.2f} excess spend"
        )
        return result

    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return {"error": handle_azure_error(e)}


def _detect_subscription_anomalies(subscription_id: str, threshold: float) -> List[Dict]:
    """
    Detect anomalies for a single subscription.
    
    Args:
        subscription_id: Azure subscription ID
        threshold: Anomaly threshold multiplier
    
    Returns:
        List of anomaly dictionaries
    """
    anomalies = []

    try:
        # Get actual costs for last 24 hours
        actual_costs = _get_actual_costs(subscription_id, days=1)

        # Get historical costs for last 7 days (excluding today)
        historical_costs = _get_actual_costs(subscription_id, days=7, offset_days=1)

        # Calculate averages by resource group and service
        historical_averages = _calculate_averages(historical_costs)

        # Compare actual vs. average
        for cost_entry in actual_costs:
            key = (cost_entry["resource_group"], cost_entry["service_name"])
            avg_cost = historical_averages.get(key, 0.0)

            if avg_cost > 0 and cost_entry["cost"] > (avg_cost * threshold):
                variance_percent = ((cost_entry["cost"] - avg_cost) / avg_cost) * 100

                anomalies.append(
                    {
                        "subscription_id": subscription_id,
                        "subscription_name": cost_entry.get("subscription_name", "Unknown"),
                        "resource_group": cost_entry["resource_group"],
                        "service_name": cost_entry["service_name"],
                        "actual_cost": round(cost_entry["cost"], 2),
                        "average_cost": round(avg_cost, 2),
                        "variance_percent": round(variance_percent, 2),
                        "date": cost_entry["date"],
                    }
                )

    except Exception as e:
        logger.error(f"Failed to detect anomalies for subscription {subscription_id[:8]}: {e}")

    return anomalies


def _get_actual_costs(
    subscription_id: str, days: int = 1, offset_days: int = 0
) -> List[Dict]:
    """
    Get actual costs for a subscription over a time period.
    
    Args:
        subscription_id: Azure subscription ID
        days: Number of days to query
        offset_days: Days to offset from today (0 = today, 1 = yesterday)
    
    Returns:
        List of cost entries with resource group, service, and cost
    """
    client_factory = get_client_factory()
    cost_client = client_factory.get_cost_management_client()

    # Calculate date range
    end_date = datetime.utcnow() - timedelta(days=offset_days)
    start_date = end_date - timedelta(days=days)

    # Build query
    scope = f"/subscriptions/{subscription_id}"
    query = QueryDefinition(
        type="ActualCost",
        timeframe="Custom",
        time_period=QueryTimePeriod(
            from_property=start_date.strftime("%Y-%m-%dT00:00:00Z"),
            to=end_date.strftime("%Y-%m-%dT23:59:59Z"),
        ),
        dataset=QueryDataset(
            granularity="Daily",
            aggregation={
                "totalCost": QueryAggregation(name="Cost", function="Sum"),
            },
            grouping=[
                QueryGrouping(type="Dimension", name="ResourceGroupName"),
                QueryGrouping(type="Dimension", name="ServiceName"),
            ],
        ),
    )

    # Execute query
    result = cost_client.query.usage(scope=scope, parameters=query)

    # Parse results
    costs = []
    if result.rows:
        for row in result.rows:
            # Row format: [cost, resource_group, service_name, date]
            costs.append(
                {
                    "cost": float(row[0]) if row[0] else 0.0,
                    "resource_group": row[1] if row[1] else "Unassigned",
                    "service_name": row[2] if row[2] else "Unknown",
                    "date": str(row[3]) if len(row) > 3 else start_date.strftime("%Y-%m-%d"),
                }
            )

    return costs


def _calculate_averages(cost_entries: List[Dict]) -> Dict[tuple, float]:
    """
    Calculate average costs by resource group and service.
    
    Args:
        cost_entries: List of cost entries
    
    Returns:
        Dictionary mapping (resource_group, service_name) to average cost
    """
    grouped_costs = {}

    for entry in cost_entries:
        key = (entry["resource_group"], entry["service_name"])
        if key not in grouped_costs:
            grouped_costs[key] = []
        grouped_costs[key].append(entry["cost"])

    # Calculate averages
    averages = {}
    for key, costs in grouped_costs.items():
        averages[key] = mean(costs) if costs else 0.0

    return averages
