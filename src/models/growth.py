"""Reusable growth and retention models."""

import pandas as pd


def build_channel_performance(customers: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    """Aggregate customers and recognized revenue by acquisition channel."""
    customer_counts = (
        customers.groupby("acquisition_channel", as_index=False)
        .agg(customers=("customer_id", "nunique"))
    )
    order_customer = orders.merge(
        customers[["customer_id", "acquisition_channel"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )
    revenue = (
        order_customer.loc[order_customer["order_status"] == "completed"]
        .groupby("acquisition_channel", as_index=False)
        .agg(
            completed_orders=("order_id", "nunique"),
            revenue=("amount", "sum"),
            purchasing_customers=("customer_id", "nunique"),
        )
    )
    result = customer_counts.merge(revenue, on="acquisition_channel", how="left")
    result[["completed_orders", "revenue", "purchasing_customers"]] = result[
        ["completed_orders", "revenue", "purchasing_customers"]
    ].fillna(0)
    result["customer_conversion_rate"] = result["purchasing_customers"].div(result["customers"].replace(0, pd.NA))
    result["revenue_per_customer"] = result["revenue"].div(result["customers"].replace(0, pd.NA))
    return result.sort_values("revenue", ascending=False).reset_index(drop=True)


def build_repeat_purchase_metrics(customers: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    """Calculate first-order and repeat-purchase behavior by signup month."""
    completed = orders.loc[orders["order_status"] == "completed"].copy()
    first_order = completed.groupby("customer_id", as_index=False)["order_date"].min().rename(columns={"order_date": "first_order_date"})
    order_counts = completed.groupby("customer_id").size().rename("completed_order_count").reset_index()

    customer_behavior = customers[["customer_id", "signup_date"]].merge(first_order, on="customer_id", how="left")
    customer_behavior = customer_behavior.merge(order_counts, on="customer_id", how="left")
    customer_behavior["completed_order_count"] = customer_behavior["completed_order_count"].fillna(0).astype(int)
    customer_behavior["signup_month"] = customer_behavior["signup_date"].dt.to_period("M").astype(str)
    customer_behavior["is_purchaser"] = customer_behavior["completed_order_count"] > 0
    customer_behavior["is_repeat_purchaser"] = customer_behavior["completed_order_count"] > 1

    return (
        customer_behavior.groupby("signup_month", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            purchasers=("is_purchaser", "sum"),
            repeat_purchasers=("is_repeat_purchaser", "sum"),
        )
        .assign(
            purchase_rate=lambda d: d["purchasers"].div(d["customers"].replace(0, pd.NA)),
            repeat_purchase_rate=lambda d: d["repeat_purchasers"].div(d["purchasers"].replace(0, pd.NA)),
        )
    )
