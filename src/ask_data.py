"""Ask a business question of the trusted growth data layer."""

import sys

from src.ai.data_assistant import classify_question, execute_intent
from src.ingestion.load_sources import load_sources
from src.transformations.staging import stage_customers, stage_marketing_events, stage_orders


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit('Usage: python -m src.ask_data "Which channel generated the most revenue?"')

    sources = load_sources()
    customers = stage_customers(sources["customers"])
    orders = stage_orders(sources["orders"])
    events = stage_marketing_events(sources["marketing_events"])

    intent = classify_question(question)
    result = execute_intent(intent, customers, orders, events)

    print(f"Intent: {intent.metric} | group_by={intent.group_by} | channel={intent.channel}")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
