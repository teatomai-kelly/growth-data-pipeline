import pandas as pd
import pytest

from src.ai.data_assistant import AnalyticsIntent, execute_intent
from src.transformations.staging import stage_customers, stage_marketing_events, stage_orders


def _sources():
    customers = stage_customers(pd.read_csv("data/raw/customers.csv"))
    orders = stage_orders(pd.read_csv("data/raw/orders.csv"))
    events = stage_marketing_events(pd.read_csv("data/raw/marketing_events.csv"))
    return customers, orders, events


def test_assistant_executes_only_supported_metric_groupings():
    customers, orders, events = _sources()
    result = execute_intent(
        AnalyticsIntent("customers_by_channel", "acquisition_channel"),
        customers,
        orders,
        events,
    )
    assert "customers" in result.columns
    assert result["customers"].sum() == customers["customer_id"].nunique()


def test_assistant_can_filter_to_one_acquisition_channel():
    customers, orders, events = _sources()
    result = execute_intent(
        AnalyticsIntent("customers_by_channel", "overall", "referral"),
        customers,
        orders,
        events,
    )
    assert result.loc[0, "customers"] == 5


def test_assistant_rejects_invalid_grouping_for_metric():
    customers, orders, events = _sources()
    with pytest.raises(ValueError):
        execute_intent(
            AnalyticsIntent("revenue_by_channel", "signup_month"),
            customers,
            orders,
            events,
        )
