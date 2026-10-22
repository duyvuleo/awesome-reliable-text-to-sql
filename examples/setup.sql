-- Entirely synthetic customers and orders, created for this tutorial.
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL UNIQUE
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    ordered_on TEXT NOT NULL,
    gross_amount_cents INTEGER NOT NULL CHECK (gross_amount_cents >= 0),
    refund_amount_cents INTEGER NOT NULL
        CHECK (refund_amount_cents BETWEEN 0 AND gross_amount_cents)
);

INSERT INTO customers VALUES
    (1, 'Amber Studio'),
    (2, 'Birch Books'),
    (3, 'Cedar Cafe');

INSERT INTO orders VALUES
    (1, 1, '2026-01-10', 10000, 8000),
    (2, 1, '2026-01-15',  8000, 6000),
    (3, 2, '2026-01-20', 12000, 1000),
    (4, 3, '2026-01-22',  9000,    0);
