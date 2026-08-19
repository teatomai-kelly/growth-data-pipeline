# Data Model

## Grain

The core analytical models use explicit grains:

- `dim_customer`: one row per customer
- `fct_order`: one row per order
- `fct_marketing_event`: one row per marketing event
- `mart_daily_growth`: one row per calendar date

## Core relationships

```text
                 dim_customer
                  customer_id
                       |
             +---------+---------+
             |                   |
             v                   v
          fct_order       fct_marketing_event
          order_id             event_id
          customer_id          customer_id
             |                   |
             +---------+---------+
                       |
                       v
               mart_daily_growth
```

## Modeling principles

1. Define grain before writing transformations.
2. Preserve source identifiers so records can be traced back to the originating system.
3. Separate source cleanup from business logic.
4. Keep dimensions and facts at stable, documented grains.
5. Calculate stakeholder-facing metrics from modeled data rather than repeatedly rebuilding joins in dashboards.

## Initial business metrics

### Acquisition

- New customers by acquisition channel
- Marketing events by event type
- Customer conversion rate

### Revenue

- Orders
- Gross revenue
- Average order value

### Retention

- Repeat customers
- Repeat-purchase rate
- Customers active within a rolling period

The model will be expanded as the synthetic source data and transformation logic are added.
