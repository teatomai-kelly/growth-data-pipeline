"""Reusable data quality checks."""

import pandas as pd


def assert_unique(df: pd.DataFrame, key: str) -> None:
    """Fail if a modeled key is duplicated."""
    if df[key].duplicated().any():
        raise AssertionError(f"Duplicate values found for key: {key}")


def assert_not_null(df: pd.DataFrame, columns: list[str]) -> None:
    """Fail if required columns contain null values."""
    null_columns = [column for column in columns if df[column].isna().any()]
    if null_columns:
        raise AssertionError(f"Null values found in required columns: {null_columns}")


def assert_non_negative(df: pd.DataFrame, column: str) -> None:
    """Fail if a numeric measure is negative."""
    if (df[column] < 0).any():
        raise AssertionError(f"Negative values found in {column}")
