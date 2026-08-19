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


@dataclass(frozen=True)
class AnalyticsIntent:
    metric: str
    group_by: str


INTENT_SCHEMA = {
    "type": "json_schema",
    "name": "analytics_intent",
    "description": "Classify a business question into an approved analytics metric and grouping.",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "metric": {
                "type": "string",
                "enum": sorted(ALLOWED_METRICS),
            },
            "group_by": {
                "type": "string",
                "enum": sorted(ALLOWED_GROUPS),
            },
        },
        "required": ["metric", "group_by"],
        "additionalProperties": False,
    },
}


SYSTEM_INSTRUCTIONS = """You are a growth analytics intent classifier.
Map a user's question to exactly one approved metric and grouping.
Never invent metrics, tables, SQL, filters, or fields.
Approved metrics: revenue_by_channel, customers_by_channel, activation_rate, repeat_purchase_rate.
Approved groupings: acquisition_channel, signup_month, overall.
"""


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
    intent = AnalyticsIntent(metric=payload["metric"], group_by=payload["group_by"])
    if intent.metric not in ALLOWED_METRICS or intent.group_by not in ALLOWED_GROUPS:
        raise ValueError("Model returned an unsupported analytics intent.")
    return intent


def execute_intent(
    intent: AnalyticsIntent,
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    """Execute an approved intent against trusted data."""
    if intent.metric == "revenue_by_channel":
        from src.models.growth import build_channel_performance
        result = build_channel_performance(customers, orders)
        return result[["acquisition_channel", "revenue", "revenue_per_customer"]]

    if intent.metric == "customers_by_channel":
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
        return result

    if intent.metric == "repeat_purchase_rate":
        from src.models.growth import build_repeat_purchase_metrics
        return build_repeat_purchase_metrics(customers, orders)

    raise ValueError(f"Unsupported metric: {intent.metric}")
