-- Create a summary table of customer orders
CREATE OR REPLACE TRANSIENT TABLE {{ params.target_table }} AS
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS total_orders,
    SUM(o.order_amount) AS total_spent,
    MAX(o.order_date) AS last_order_date
FROM
    {{ params.source_table }} o
JOIN
    raw.customers c ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
HAVING
    total_orders > 0;
