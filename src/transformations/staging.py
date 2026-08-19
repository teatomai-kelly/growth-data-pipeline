"""Standardize source fields before business transformations."""

import pandas as pd


def stage_customers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["signup_date"] = pd.to_datetime(out["signup_date"], errors="raise")
    out["acquisition_channel"] = out["acquisition_channel"].str.strip().str.lower()
    out["country"] = out["country"].str.strip().str.upper()
    out["plan"] = out["plan"].str.strip().str.lower()
    return out


def stage_orders(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["order_date"] = pd.to_datetime(out["order_date"], errors="raise")
    out["order_status"] = out["order_status"].str.strip().str.lower()
    out["amount"] = pd.to_numeric(out["amount"], errors="raise")
    return out


def stage_marketing_events(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["event_date"] = pd.to_datetime(out["event_date"], errors="raise")
    out["event_type"] = out["event_type"].str.strip().str.lower()
    out["channel"] = out["channel"].str.strip().str.lower()
    return out
