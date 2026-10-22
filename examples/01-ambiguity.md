# 1. Ambiguity and clarification

[All walkthroughs](README.md) · [Run the example](run.py)

**Request:** “Which customer had the highest sales in January 2026?”

“Sales” can reasonably mean gross billed amounts or amounts remaining after refunds. The provided question does not choose between them, and both quantities are present in the toy schema.

| Interpretation | SQL | Result |
| --- | --- | --- |
| Sum gross order amounts | [gross_sales.sql](sql/gross_sales.sql) | Amber Studio, 180.00 |
| Subtract each order's refunds | [net_sales.sql](sql/net_sales.sql) | Birch Books, 110.00 |

Both queries execute successfully. Their different results show why executing one plausible query cannot establish that it answers the intended question.

The scripted clarification is:

> **Assistant:** Do you mean gross sales, or sales after refunds?
>
> **User:** Sales after refunds.
>
> **Assistant:** Birch Books had the highest sales after refunds in January 2026: 110.00.

The user reply selects the net-sales interpretation. The corresponding query is:

```sql
WITH sales AS (
    SELECT c.customer_name,
           SUM(o.gross_amount_cents - o.refund_amount_cents) AS sales_cents
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
```

Run `python3 examples/run.py --example ambiguity` from the repository root to execute both interpretations and verify the documented answers. The clarification is predefined; the script does not detect arbitrary ambiguity or generate questions.

**Read next:** [AmbiQT and interpretation coverage](../papers/README.md#ambiqt), [AMBROSIA](../papers/README.md#ambrosia), and [ABISS and interactive evaluation](../papers/README.md#abiss). These papers evaluate different tasks; the [matrix](../docs/benchmark-matrix.md) explains the distinction.
