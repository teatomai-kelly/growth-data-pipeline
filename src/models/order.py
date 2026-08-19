"""Order fact model."""

import pandas as pd


VALID_REVENUE_STATUSES = {"completed"}


def build_fct_order(orders: pd.DataFrame) -> pd.DataFrame:
    """Build one row per order and calculate recognized revenue."""
    fact = orders.copy()
    fact["recognized_revenue"] = fact["amount"].where(
        fact["order_status"].isin(VALID_REVENUE_STATUSES), 0.0
    )
    fact["is_completed"] = fact["order_status"].eq("completed")
    return fact
