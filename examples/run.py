#!/usr/bin/env python3
"""Run three offline, scripted Text-to-SQL examples against synthetic SQLite data."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def create_database():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript((ROOT / "setup.sql").read_text(encoding="utf-8"))
    connection.execute("PRAGMA query_only = ON")
    return connection


def execute(connection, filename):
    query = (ROOT / "sql" / filename).read_text(encoding="utf-8")
    return connection.execute(query).fetchall()


def schema_columns(connection):
    """Read the actual toy schema; do not invent an unavailable field."""
    columns = set()
    for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
        for row in connection.execute("SELECT name FROM pragma_table_info(?)", (name,)):
            columns.add((name, row[0]))
    return columns


def money(cents):
    return f"{cents // 100}.{cents % 100:02d}"


def ambiguity(connection):
    gross = execute(connection, "gross_sales.sql")
    net = execute(connection, "net_sales.sql")
    expected_gross = [("Amber Studio", 18000)]
    expected_net = [("Birch Books", 11000)]
    if gross != expected_gross or net != expected_net or gross == net:
        raise ValueError("The two interpretations no longer produce the documented answers.")
    print("1. Ambiguity and clarification")
    print("   Request: Which customer had the highest sales in January 2026?")
    print(f"   Gross sales: {gross[0][0]} ({money(gross[0][1])})")
    print(f"   After refunds: {net[0][0]} ({money(net[0][1])})")
    print("   Ask: Do you mean gross sales, or sales after refunds?")
    print("   Scripted user reply: Sales after refunds.")
    print(f"   Confirmed interpretation: {net[0][0]} ({money(net[0][1])})")
    print("   PASS: both SQL interpretations execute and their answers differ.")


def unsupported(connection):
    columns = schema_columns(connection)
    if ("customers", "customer_name") not in columns or ("customers", "email_address") in columns:
        raise ValueError("The example schema no longer has the documented missing field.")
    print("2. Unsupported information")
    print("   Request: List every customer's email address.")
    print("   Schema check: customer_name is present; email_address is absent.")
    print("   Response: I cannot retrieve email addresses from the provided database.")
    print("   Next step: provide an authorized source containing that field.")
    print("   PASS: the required field is missing; no answer SQL is emitted.")


def empty_result(connection):
    if "orders" not in {name for name, in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}:
        raise ValueError("The orders table is missing.")
    rows = execute(connection, "february_orders.sql")
    january_count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    if rows != [] or january_count != 4:
        raise ValueError("The query no longer has the documented empty result over four stored orders.")
    print("3. A valid empty result")
    print("   Request: List the orders placed in February 2026.")
    print("   Query: a SELECT using the existing ordered_on column.")
    print("   Result: 0 rows.")
    print("   Response: No orders match February 2026 in this database snapshot.")
    print("   PASS: the query succeeds; an empty result is not a missing-schema error.")


EXAMPLES = {"ambiguity": ambiguity, "unsupported": unsupported, "empty": empty_result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", choices=["all", *EXAMPLES], default="all")
    parser.add_argument("--check", action="store_true", help="verify the documented outcomes; return nonzero on failure")
    args = parser.parse_args()
    selected = EXAMPLES if args.example == "all" else {args.example: EXAMPLES[args.example]}
    connection = create_database()
    print("Synthetic SQLite walkthroughs. SQL, dialogue and decisions are scripted; no model is called.\n")
    try:
        for index, example in enumerate(selected.values()):
            if index:
                print()
            example(connection)
    except (OSError, sqlite3.Error, ValueError) as error:
        parser.exit(1, f"Example check failed: {error}\n")
    finally:
        connection.close()
    if args.check:
        print(f"\nVerified {len(selected)} example(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
