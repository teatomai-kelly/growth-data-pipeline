"""Orchestrate the local growth data pipeline."""

from pathlib import Path

from src.ingestion.load_sources import load_sources
from src.models.customer import build_dim_customer
from src.models.growth import build_channel_performance, build_repeat_purchase_metrics
from src.models.marketing_event import build_fct_marketing_event
from src.models.order import build_fct_order
from src.quality.checks import assert_non_negative, assert_not_null, assert_unique
from src.transformations.growth_metrics import build_daily_growth_metrics
from src.transformations.staging import (
    stage_customers,
    stage_marketing_events,
    stage_orders,
)


OUTPUT_DIR = Path("data/processed")


def run() -> None:
    sources = load_sources()

    customers = stage_customers(sources["customers"])
    orders = stage_orders(sources["orders"])
    events = stage_marketing_events(sources["marketing_events"])

    dim_customer = build_dim_customer(customers)
    fct_order = build_fct_order(orders)
    fct_event = build_fct_marketing_event(events)
    daily_growth = build_daily_growth_metrics(customers, orders, events)
    channel_performance = build_channel_performance(customers, orders)
    repeat_purchase = build_repeat_purchase_metrics(customers, orders)

    assert_unique(dim_customer, "customer_id")
    assert_unique(fct_order, "order_id")
    assert_unique(fct_event, "event_id")
    assert_not_null(dim_customer, ["customer_id", "signup_date"])
    assert_non_negative(fct_order, "amount")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dim_customer.to_csv(OUTPUT_DIR / "dim_customer.csv", index=False)
    fct_order.to_csv(OUTPUT_DIR / "fct_order.csv", index=False)
    fct_event.to_csv(OUTPUT_DIR / "fct_marketing_event.csv", index=False)
    daily_growth.to_csv(OUTPUT_DIR / "mart_daily_growth.csv", index=False)
    channel_performance.to_csv(OUTPUT_DIR / "mart_channel_performance.csv", index=False)
    repeat_purchase.to_csv(OUTPUT_DIR / "mart_repeat_purchase.csv", index=False)

    print(f"Pipeline complete. Wrote {len(daily_growth)} daily metric rows.")


if __name__ == "__main__":
    run()
