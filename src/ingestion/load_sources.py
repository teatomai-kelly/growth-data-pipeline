"""Load and lightly standardize raw CSV sources."""

from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = {
    "customers": {"customer_id", "signup_date", "acquisition_channel", "country", "plan"},
    "orders": {"order_id", "customer_id", "order_date", "order_status", "amount"},
    "marketing_events": {"event_id", "customer_id", "event_date", "event_type", "channel"},
}


def load_csv(path: str | Path, dataset: str) -> pd.DataFrame:
    """Load a source file and validate its required columns."""
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS[dataset] - set(frame.columns)
    if missing:
        raise ValueError(f"{dataset}: missing required columns: {sorted(missing)}")
    return frame


def load_sources(raw_dir: str | Path = "data/raw") -> dict[str, pd.DataFrame]:
    """Load all source datasets into memory."""
    raw_dir = Path(raw_dir)
    return {
        "customers": load_csv(raw_dir / "customers.csv", "customers"),
        "orders": load_csv(raw_dir / "orders.csv", "orders"),
        "marketing_events": load_csv(raw_dir / "marketing_events.csv", "marketing_events"),
    }
