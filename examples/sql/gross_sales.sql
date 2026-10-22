WITH sales AS (
    SELECT c.customer_name,
           SUM(o.gross_amount_cents) AS sales_cents
    FROM orders AS o
    JOIN customers AS c USING (customer_id)
    WHERE o.ordered_on >= '2026-01-01'
      AND o.ordered_on <  '2026-02-01'
    GROUP BY c.customer_id, c.customer_name
)
SELECT customer_name, sales_cents
FROM sales
WHERE sales_cents = (SELECT MAX(sales_cents) FROM sales)
ORDER BY customer_name;
