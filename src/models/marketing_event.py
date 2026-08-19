"""Marketing event fact model."""

import pandas as pd


def build_fct_marketing_event(events: pd.DataFrame) -> pd.DataFrame:
    """Build one row per marketing event with derived event flags."""
    fact = events.copy()
    fact["is_signup"] = fact["event_type"].eq("signup")
    fact["is_activation"] = fact["event_type"].eq("activation")
    return fact
