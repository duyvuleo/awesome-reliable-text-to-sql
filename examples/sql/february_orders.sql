SELECT order_id, customer_id, ordered_on, gross_amount_cents
FROM orders
WHERE ordered_on >= '2026-02-01'
  AND ordered_on <  '2026-03-01'
ORDER BY order_id;
