"""Natural-language analytics assistant.

The model is used only to interpret a business question into a constrained
analytics intent. Python executes the metric against trusted modeled data;
the model never receives permission to generate or execute arbitrary SQL.

OpenAI integration is optional. Set OPENAI_API_KEY to enable it.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import pandas as pd


ALLOWED_METRICS = {
    "revenue_by_channel",
    "customers_by_channel",
    "activation_rate",
    "repeat_purchase_rate",
}
ALLOWED_GROUPS = {"acquisition_channel", "signup_month", "overall"}
ALLOWED_CHANNELS = {"all", "organic", "paid_search", "paid_social", "referral"}
ALLOWED_GROUPS_BY_METRIC = {
    "revenue_by_channel": {"acquisition_channel", "overall"},
    "customers_by_channel": {"acquisition_channel", "overall"},
    "activation_rate": {"acquisition_channel", "overall"},
    "repeat_purchase_rate": {"signup_month", "overall"},
}


@dataclass(frozen=True)
class AnalyticsIntent:
    metric: str
    group_by: str
    channel: str = "all"


INTENT_SCHEMA = {
    "type": "json_schema",
    "name": "analytics_intent",
    "description": "Classify a business question into an approved analytics metric, grouping, and optional acquisition channel filter.",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "metric": {"type": "string", "enum": sorted(ALLOWED_METRICS)},
            "group_by": {"type": "string", "enum": sorted(ALLOWED_GROUPS)},
            "channel": {"type": "string", "enum": sorted(ALLOWED_CHANNELS)},
        },
        "required": ["metric", "group_by", "channel"],
        "additionalProperties": False,
    },
}


SYSTEM_INSTRUCTIONS = """You are a growth analytics intent classifier.
Map a user's question to exactly one approved metric, grouping, and optional acquisition-channel filter.
Never invent metrics, tables, SQL, filters, or fields.
Approved metrics: revenue_by_channel, customers_by_channel, activation_rate, repeat_purchase_rate.
Valid groupings by metric:
- revenue_by_channel: acquisition_channel or overall
- customers_by_channel: acquisition_channel or overall
- activation_rate: acquisition_channel or overall
- repeat_purchase_rate: signup_month or overall
Approved channels: all, organic, paid_search, paid_social, referral.
Use channel='all' when the user did not request a specific acquisition channel.
"""


def _validate_intent(intent: AnalyticsIntent) -> None:
    if intent.metric not in ALLOWED_METRICS:
        raise ValueError("Unsupported analytics metric.")
    if intent.group_by not in ALLOWED_GROUPS_BY_METRIC[intent.metric]:
        raise ValueError("Unsupported grouping for the selected metric.")
    if intent.channel not in ALLOWED_CHANNELS:
        raise ValueError("Unsupported acquisition channel.")


def classify_question(question: str) -> AnalyticsIntent:
    """Use an LLM to classify a question into the constrained semantic layer."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the optional 'openai' dependency to use the AI assistant.") from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required to use the AI assistant.")

    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        instructions=SYSTEM_INSTRUCTIONS,
        input=question,
        text={"format": INTENT_SCHEMA},
    )
    payload = json.loads(response.output_text)
    intent = AnalyticsIntent(
        metric=payload["metric"],
        group_by=payload["group_by"],
        channel=payload["channel"],
    )
    _validate_intent(intent)
    return intent


def _filter_channel(df: pd.DataFrame, channel: str) -> pd.DataFrame:
    if channel == "all":
        return df
    return df.loc[df["acquisition_channel"] == channel].copy()


def execute_intent(
    intent: AnalyticsIntent,
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    """Execute an approved intent against trusted data."""
    _validate_intent(intent)
    customers = _filter_channel(customers, intent.channel)
    customer_ids = set(customers["customer_id"])
    orders = orders.loc[orders["customer_id"].isin(customer_ids)].copy()
    events = events.loc[events["customer_id"].isin(customer_ids)].copy()

    if intent.metric == "revenue_by_channel":
        from src.models.growth import build_channel_performance
        result = build_channel_performance(customers, orders)
        if intent.group_by == "overall":
            customer_count = result["customers"].sum()
            return pd.DataFrame([{
                "revenue": result["revenue"].sum(),
                "revenue_per_customer": result["revenue"].sum() / customer_count if customer_count else None,
            }])
        return result[["acquisition_channel", "revenue", "revenue_per_customer"]]

    if intent.metric == "customers_by_channel":
        if intent.group_by == "overall":
            return pd.DataFrame([{"customers": customers["customer_id"].nunique()}])
        return (
            customers.groupby("acquisition_channel", as_index=False)
            .agg(customers=("customer_id", "nunique"))
            .sort_values("customers", ascending=False)
        )

    if intent.metric == "activation_rate":
        signups = customers.groupby("acquisition_channel")["customer_id"].nunique().rename("signups")
        activations = (
            events.loc[events["event_type"] == "activation"]
            .merge(customers[["customer_id", "acquisition_channel"]], on="customer_id", how="left", validate="many_to_one")
            .groupby("acquisition_channel")["customer_id"]
            .nunique()
            .rename("activations")
        )
        result = pd.concat([signups, activations], axis=1).fillna(0).reset_index()
        result["activation_rate"] = result["activations"].div(result["signups"].replace(0, pd.NA))
        if intent.group_by == "overall":
            signups_total = result["signups"].sum()
            return pd.DataFrame([{
                "signups": signups_total,
                "activations": result["activations"].sum(),
                "activation_rate": result["activations"].sum() / signups_total if signups_total else None,
            }])
        return result

    if intent.metric == "repeat_purchase_rate":
        from src.models.growth import build_repeat_purchase_metrics
        result = build_repeat_purchase_metrics(customers, orders)
        if intent.group_by == "overall":
            purchasers = result["purchasers"].sum()
            repeats = result["repeat_purchasers"].sum()
            return pd.DataFrame([{
                "purchasers": purchasers,
                "repeat_purchasers": repeats,
                "repeat_purchase_rate": repeats / purchasers if purchasers else None,
            }])
        return result

    raise ValueError(f"Unsupported metric: {intent.metric}")
