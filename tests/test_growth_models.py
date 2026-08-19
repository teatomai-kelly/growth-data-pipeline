from src.models.growth import build_channel_performance, build_repeat_purchase_metrics
from src.transformations.staging import stage_customers, stage_orders


def test_channel_performance_preserves_all_acquisition_channels():
    customers = stage_customers(__import__("pandas").read_csv("data/raw/customers.csv"))
    orders = stage_orders(__import__("pandas").read_csv("data/raw/orders.csv"))
    result = build_channel_performance(customers, orders)
    assert set(result["acquisition_channel"]) == set(customers["acquisition_channel"])
    assert (result["revenue"] >= 0).all()


def test_repeat_purchase_metrics_identifies_repeat_customers():
    customers = stage_customers(__import__("pandas").read_csv("data/raw/customers.csv"))
    orders = stage_orders(__import__("pandas").read_csv("data/raw/orders.csv"))
    result = build_repeat_purchase_metrics(customers, orders)
    assert "repeat_purchase_rate" in result.columns
    assert (result["repeat_purchasers"] >= 0).all()
