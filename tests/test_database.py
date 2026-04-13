"""Unit tests for the DatabaseManager class using in-memory SQLite."""

import unittest
from datetime import datetime

from src.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Tests for DatabaseManager."""

    def setUp(self) -> None:
        """Create a fresh in-memory database before each test."""
        self.db = DatabaseManager(connection_string="sqlite:///:memory:")
        self.db.create_tables()

    def tearDown(self) -> None:
        """Close the database connection after each test."""
        self.db.close()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def test_create_tables(self) -> None:
        """create_tables() succeeds without raising and is idempotent."""
        # Calling twice should not raise
        self.db.create_tables()

    # ------------------------------------------------------------------
    # Product insertion / retrieval
    # ------------------------------------------------------------------

    def test_insert_product(self) -> None:
        """A single product can be inserted and its ID returned."""
        product_id = self.db.insert_product({
            "name": "Test Widget",
            "price": 9.99,
            "brand": "TestCo",
            "url": "https://example.com/widget",
            "image_url": "https://example.com/widget.jpg",
            "rating": 4.5,
            "stock": "In Stock",
        })
        self.assertIsInstance(product_id, int)
        self.assertGreater(product_id, 0)

    def test_insert_product_ignores_unknown_keys(self) -> None:
        """Unknown keys in the data dict are silently ignored."""
        product_id = self.db.insert_product({
            "name": "Widget",
            "unknown_field": "should be ignored",
        })
        self.assertIsInstance(product_id, int)

    def test_get_products(self) -> None:
        """Inserted products are returned by get_products()."""
        self.db.insert_product({"name": "Alpha", "price": 1.0})
        self.db.insert_product({"name": "Beta", "price": 2.0})
        products = self.db.get_products()
        self.assertEqual(len(products), 2)
        names = {p["name"] for p in products}
        self.assertIn("Alpha", names)
        self.assertIn("Beta", names)

    def test_get_products_with_filter(self) -> None:
        """Filter by an exact column value."""
        self.db.insert_product({"name": "Alpha", "brand": "BrandA"})
        self.db.insert_product({"name": "Beta", "brand": "BrandB"})
        results = self.db.get_products(filters={"brand": "BrandA"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Alpha")

    def test_get_products_limit(self) -> None:
        """The limit parameter caps the number of rows returned."""
        for i in range(5):
            self.db.insert_product({"name": f"Item {i}"})
        results = self.db.get_products(limit=3)
        self.assertEqual(len(results), 3)

    def test_get_products_empty(self) -> None:
        """An empty table returns an empty list."""
        results = self.db.get_products()
        self.assertEqual(results, [])

    def test_product_schema_fields(self) -> None:
        """Every expected schema column is present in a returned row."""
        self.db.insert_product({"name": "Schema Test"})
        product = self.db.get_products()[0]
        expected_keys = {"id", "name", "price", "brand", "url", "image_url",
                         "rating", "stock", "created_at", "updated_at"}
        self.assertTrue(expected_keys.issubset(product.keys()))

    # ------------------------------------------------------------------
    # Batch insertion
    # ------------------------------------------------------------------

    def test_insert_products_batch(self) -> None:
        """Batch insertion returns the correct record count."""
        products = [
            {"name": f"Product {i}", "price": float(i)} for i in range(10)
        ]
        count = self.db.insert_products_batch(products)
        self.assertEqual(count, 10)
        all_products = self.db.get_products(limit=100)
        self.assertEqual(len(all_products), 10)

    def test_insert_products_batch_empty(self) -> None:
        """Empty batch returns 0 without raising."""
        count = self.db.insert_products_batch([])
        self.assertEqual(count, 0)

    # ------------------------------------------------------------------
    # Scrape logs
    # ------------------------------------------------------------------

    def test_log_scrape(self) -> None:
        """A scrape session can be logged and its ID returned."""
        log_id = self.db.log_scrape(
            domain="example.com",
            status="success",
            records_extracted=42,
        )
        self.assertIsInstance(log_id, int)
        self.assertGreater(log_id, 0)

    def test_log_scrape_with_errors(self) -> None:
        """Error messages are stored correctly."""
        log_id = self.db.log_scrape(
            domain="broken.com",
            status="failed",
            records_extracted=0,
            errors="ConnectionError: timeout",
        )
        logs = self.db.get_scrape_logs(domain="broken.com")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["errors"], "ConnectionError: timeout")

    def test_get_scrape_logs(self) -> None:
        """All logged sessions are returned."""
        self.db.log_scrape("site-a.com", "success", 10)
        self.db.log_scrape("site-b.com", "failed", 0)
        logs = self.db.get_scrape_logs()
        self.assertEqual(len(logs), 2)

    def test_get_scrape_logs_filtered(self) -> None:
        """Logs can be filtered by domain."""
        self.db.log_scrape("site-a.com", "success", 5)
        self.db.log_scrape("site-b.com", "success", 3)
        logs = self.db.get_scrape_logs(domain="site-a.com")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["domain"], "site-a.com")

    def test_scrape_log_schema_fields(self) -> None:
        """Every expected log column is present in a returned row."""
        self.db.log_scrape("check.com", "success", 1)
        log = self.db.get_scrape_logs()[0]
        expected_keys = {"id", "domain", "timestamp", "status",
                         "records_extracted", "errors"}
        self.assertTrue(expected_keys.issubset(log.keys()))

    def test_get_scrape_logs_order(self) -> None:
        """Logs are returned in descending timestamp order."""
        self.db.log_scrape("first.com", "success", 1)
        self.db.log_scrape("second.com", "success", 2)
        logs = self.db.get_scrape_logs()
        # Most recently inserted entry should appear first
        self.assertEqual(logs[0]["domain"], "second.com")


if __name__ == "__main__":
    unittest.main()
