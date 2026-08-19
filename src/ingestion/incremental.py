"""Simple watermark-based incremental processing utilities."""

import pandas as pd


def filter_incremental(
    df: pd.DataFrame,
    date_column: str,
    last_watermark: str | None = None,
) -> pd.DataFrame:
    """Return records newer than the previous successful watermark.

    A null watermark represents an initial full load. The comparison is
    exclusive so a previously processed boundary record is not duplicated.
    """
    if last_watermark is None:
        return df.copy()

    watermark = pd.Timestamp(last_watermark)
    dates = pd.to_datetime(df[date_column], errors="raise")
    return df.loc[dates > watermark].copy()
