# Worked examples

[Back to the collection](../README.md) · [Choose a benchmark](../docs/benchmark-matrix.md)

Three small walkthroughs make the differences between ambiguity, unsupported information, and an empty answer concrete. They use an original, synthetic retail database. All SQL, clarification turns, and decisions are scripted to illustrate the concepts; these examples do not evaluate an LLM or reproduce a paper's results.

## Run in a few minutes

From the repository root, run:

```bash
python3 examples/run.py
```

Python 3.10 or later with SQLite is sufficient. No packages, credentials, network access, or downloaded datasets are needed. Each run creates an in-memory database and closes it when finished.

| Walkthrough | Request | What to notice |
| --- | --- | --- |
| [1. Ambiguity and clarification](01-ambiguity.md) | Which customer had the highest sales in January 2026? | Gross sales and sales after refunds produce different winners. Clarification selects the intended metric. |
| [2. Unsupported information](02-unsupported.md) | List every customer's email address. | The schema has no email field. Do not invent one or substitute customer names. |
| [3. A valid empty result](03-empty-result.md) | List the orders placed in February 2026. | The query is supported and executes successfully, returning zero rows in this snapshot. |

To run one walkthrough or verify all documented outcomes:

```bash
python3 examples/run.py --example ambiguity
python3 examples/run.py --example unsupported
python3 examples/run.py --example empty
python3 examples/run.py --check
```

## The toy database

[setup.sql](setup.sql) defines two tables:

- `customers(customer_id, customer_name)`
- `orders(order_id, customer_id, ordered_on, gross_amount_cents, refund_amount_cents)`

All dates are ISO-formatted dates. Amounts use integer cents. The fixture contains four January orders for three fictional customers, with refunds attributed to the corresponding order for this tutorial. An application with separate refund dates would need an explicit accounting-period rule.

| Customer | January gross sales | Refunds | January sales after refunds |
| --- | --- | --- | --- |
| Amber Studio | 180.00 | 140.00 | 40.00 |
| Birch Books | 120.00 | 10.00 | 110.00 |
| Cedar Cafe | 90.00 | 0.00 | 90.00 |

The walkthroughs hold the period and database snapshot fixed, and return all customers tied for the maximum. This isolates the choice of sales definition. The [SQL files](sql/) are readable independently of the Python runner.

For research experiments, use the [benchmark matrix](../docs/benchmark-matrix.md) and its source-specific protocols. These illustrative cases are not an evaluation dataset or evidence of model reliability.
