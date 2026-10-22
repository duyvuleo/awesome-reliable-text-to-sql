# 3. A valid empty result

[All walkthroughs](README.md) · [Run the example](run.py)

**Request:** “List the orders placed in February 2026.”

The table and date column exist. All four orders in the toy snapshot were placed in January, so a query for February is valid and returns zero rows.

```sql
SELECT order_id, customer_id, ordered_on, gross_amount_cents
FROM orders
WHERE ordered_on >= '2026-02-01'
  AND ordered_on <  '2026-03-01'
ORDER BY order_id;
```

| Query outcome | What it supports |
| --- | --- |
| Executes successfully and returns zero rows | No stored orders match February 2026 in this snapshot. |

The scripted response is:

> No orders match February 2026 in this database snapshot.

Run `python3 examples/run.py --example empty` from the repository root to execute [the query](sql/february_orders.sql) and verify that it returns an empty result over the non-empty fixture.

An empty result is different from the [missing-field case](02-unsupported.md). It also does not prove that no orders occurred outside this snapshot. In a real system, data completeness, freshness, date interpretation, and the query itself may need checking before making a broader claim.

**Read next:** [The evaluation guide](../docs/evaluation.md), [distilled SQL test suites](../papers/README.md#test-suites), and [SpotIt](../papers/README.md#spotit). Agreement or emptiness on one database instance does not establish correctness across other instances.
