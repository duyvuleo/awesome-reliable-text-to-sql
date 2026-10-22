"""Check SQL behavior at ties and period boundaries in the original toy examples."""

import importlib.util
import unittest
from pathlib import Path


module_path = Path(__file__).resolve().parent.parent / "examples" / "run.py"
spec = importlib.util.spec_from_file_location("worked_examples", module_path)
examples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(examples)


class ExampleSQLTests(unittest.TestCase):
    def setUp(self):
        self.connection = examples.create_database()
        self.addCleanup(self.connection.close)
        self.connection.execute("PRAGMA query_only = OFF")

    def test_gross_sales_returns_all_customers_tied_for_first(self):
        self.connection.execute("INSERT INTO orders VALUES (5, 2, '2026-01-31', 6000, 0)")
        self.assertEqual([("Amber Studio", 18000), ("Birch Books", 18000)],
                         examples.execute(self.connection, "gross_sales.sql"))

    def test_net_sales_returns_all_customers_tied_for_first(self):
        self.connection.execute("INSERT INTO orders VALUES (5, 3, '2026-01-31', 2000, 0)")
        self.assertEqual([("Birch Books", 11000), ("Cedar Cafe", 11000)],
                         examples.execute(self.connection, "net_sales.sql"))

    def test_february_query_includes_first_day_and_excludes_march(self):
        self.connection.executemany("INSERT INTO orders VALUES (?, 1, ?, 100, 0)",
                                    [(5, "2026-02-01"), (6, "2026-02-28"), (7, "2026-03-01")])
        self.assertEqual([5, 6], [row[0] for row in examples.execute(self.connection, "february_orders.sql")])


if __name__ == "__main__":
    unittest.main()
