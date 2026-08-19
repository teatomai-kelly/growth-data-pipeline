"""Build stakeholder-facing growth metrics from modeled data."""

import pandas as pd


def build_daily_growth_metrics(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    """Return one row per calendar date with acquisition, activation, and revenue KPIs."""
    dates = pd.concat(
        [
            customers[["signup_date"]].rename(columns={"signup_date": "date"}),
            orders[["order_date"]].rename(columns={"order_date": "date"}),
            events[["event_date"]].rename(columns={"event_date": "date"}),
        ],
        ignore_index=True,
    )
    calendar = pd.DataFrame({"date": pd.date_range(dates["date"].min(), dates["date"].max())})

    new_customers = (
        customers.groupby("signup_date", as_index=False)
        .agg(new_customers=("customer_id", "nunique"))
        .rename(columns={"signup_date": "date"})
    )

    activations = (
        events.loc[events["event_type"] == "activation"]
        .groupby("event_date", as_index=False)
        .agg(activated_customers=("customer_id", "nunique"))
        .rename(columns={"event_date": "date"})
    )

    revenue = (
        orders.loc[orders["order_status"] == "completed"]
        .groupby("order_date", as_index=False)
        .agg(
            completed_orders=("order_id", "nunique"),
            gross_revenue=("amount", "sum"),
        )
        .rename(columns={"order_date": "date"})
    )

    mart = calendar.merge(new_customers, on="date", how="left")
    mart = mart.merge(activations, on="date", how="left")
    mart = mart.merge(revenue, on="date", how="left")

    for column in ["new_customers", "activated_customers", "completed_orders"]:
        mart[column] = mart[column].fillna(0).astype(int)
    mart["gross_revenue"] = mart["gross_revenue"].fillna(0.0)
    mart["activation_rate"] = mart["activated_customers"].div(mart["new_customers"].replace(0, pd.NA))
    mart["average_order_value"] = mart["gross_revenue"].div(mart["completed_orders"].replace(0, pd.NA))
    return mart
