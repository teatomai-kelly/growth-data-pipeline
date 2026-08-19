-- Analytics-ready daily growth mart.
-- Grain: one row per calendar date.

WITH calendar AS (
    SELECT DISTINCT signup_date AS date
    FROM stg_customers
    UNION
    SELECT DISTINCT order_date AS date
    FROM stg_orders
    UNION
    SELECT DISTINCT event_date AS date
    FROM stg_marketing_events
),

new_customers AS (
    SELECT
        signup_date AS date,
        COUNT(DISTINCT customer_id) AS new_customers
    FROM stg_customers
    GROUP BY signup_date
),

activations AS (
    SELECT
        event_date AS date,
        COUNT(DISTINCT customer_id) AS activated_customers
    FROM stg_marketing_events
    WHERE event_type = 'activation'
    GROUP BY event_date
),

revenue AS (
    SELECT
        order_date AS date,
        COUNT(DISTINCT order_id) AS completed_orders,
        SUM(amount) AS gross_revenue
    FROM stg_orders
    WHERE order_status = 'completed'
    GROUP BY order_date
)

SELECT
    c.date,
    COALESCE(n.new_customers, 0) AS new_customers,
    COALESCE(a.activated_customers, 0) AS activated_customers,
    COALESCE(r.completed_orders, 0) AS completed_orders,
    COALESCE(r.gross_revenue, 0) AS gross_revenue,
    a.activated_customers * 1.0 / NULLIF(n.new_customers, 0) AS activation_rate,
    r.gross_revenue * 1.0 / NULLIF(r.completed_orders, 0) AS average_order_value
FROM calendar c
LEFT JOIN new_customers n ON c.date = n.date
LEFT JOIN activations a ON c.date = a.date
LEFT JOIN revenue r ON c.date = r.date
ORDER BY c.date;
