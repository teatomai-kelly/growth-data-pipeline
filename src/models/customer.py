"""Customer dimension model."""

import pandas as pd


def build_dim_customer(customers: pd.DataFrame) -> pd.DataFrame:
    """Build one row per customer with normalized business attributes."""
    columns = [
        "customer_id",
        "signup_date",
        "acquisition_channel",
        "country",
        "plan",
    ]
    dim = customers[columns].drop_duplicates(subset=["customer_id"]).copy()
    dim["signup_month"] = dim["signup_date"].dt.to_period("M").astype(str)
    dim["is_pro"] = dim["plan"].eq("pro")
    return dim
