import pandas as pd

from src.ingestion.incremental import filter_incremental


def test_incremental_filter_excludes_processed_watermark():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "order_id": [1, 2, 3],
        }
    )

    result = filter_incremental(df, "order_date", "2026-01-02")

    assert result["order_id"].tolist() == [3]


def test_incremental_filter_returns_full_load_without_watermark():
    df = pd.DataFrame({"event_date": ["2026-01-01", "2026-01-02"]})

    result = filter_incremental(df, "event_date")

    assert len(result) == 2
