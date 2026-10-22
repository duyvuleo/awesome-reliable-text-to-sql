# 2. Unsupported information

[All walkthroughs](README.md) · [Run the example](run.py)

**Request:** “List every customer's email address.”

The toy database has customer identifiers and names, but no email field and no linked contact source. The information required for this request is absent from the provided schema.

| Available | Required | Appropriate response |
| --- | --- | --- |
| `customers.customer_id`, `customers.customer_name` | A source of customer email addresses | Explain the missing information and request an authorized source if the user wants to continue. |

The scripted response is:

> I cannot retrieve email addresses from the provided database. An authorized contact source containing that field is needed to answer this request.

The runner inspects the actual SQLite schema, verifies that `customer_name` exists and `email_address` does not, and emits no answer SQL. It does not invent an `email_address` column, guess addresses, or return names as a substitute.

Run `python3 examples/run.py --example unsupported` from the repository root to verify the schema condition. This example uses a predefined required field; it is not a general natural-language answerability classifier.

The conclusion is limited to the provided data and capability setting. A different authorized database or tool could make the request answerable. Asking the user to rephrase cannot supply a missing contact dataset by itself.

**Read next:** [TriageSQL and question-intention classification](../papers/README.md#triagesql), [TrustSQL and answer/abstain evaluation](../papers/README.md#trustsql), and [the answerability routes in the matrix](../docs/benchmark-matrix.md#choose-a-starting-point).
