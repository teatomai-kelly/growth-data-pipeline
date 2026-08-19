import pandas as pd
import pytest

from src.ingestion.load_sources import load_sources
from src.models.customer import build_dim_customer
from src.models.order import build_fct_order
from src.quality.checks import assert_non_negative, assert_not_null, assert_unique
from src.transformations.staging import (
    stage_customers,
    stage_marketing_events,
    stage_orders,
)


@pytest.fixture(scope="module")
def pipeline_data():
    sources = load_sources()
    customers = stage_customers(sources["customers"])
    orders = stage_orders(sources["orders"])
    events = stage_marketing_events(sources["marketing_events"])
    return customers, orders, events


def test_customer_dimension_has_unique_customer_ids(pipeline_data):
    customers, _, _ = pipeline_data
    dim_customer = build_dim_customer(customers)
    assert_unique(dim_customer, "customer_id")
    assert_not_null(dim_customer, ["customer_id", "signup_date", "acquisition_channel"])


def test_orders_have_non_negative_amounts(pipeline_data):
    _, orders, _ = pipeline_data
    assert_non_negative(orders, "amount")


def test_recognized_revenue_excludes_non_completed_orders(pipeline_data):
    _, orders, _ = pipeline_data
    fact_order = build_fct_order(orders)
    refunded = fact_order.loc[fact_order["order_status"] == "refunded", "recognized_revenue"]
    cancelled = fact_order.loc[fact_order["order_status"] == "cancelled", "recognized_revenue"]
    assert (refunded == 0).all()
    assert (cancelled == 0).all()


def test_marketing_events_reference_known_customers(pipeline_data):
    customers, _, events = pipeline_data
    assert set(events["customer_id"]).issubset(set(customers["customer_id"]))
