"""Unit tests for the DataExtractor class."""

import unittest

from src.extractor import DataExtractor

PRODUCT_HTML = """<!DOCTYPE html>
<html>
<head><title>Test Shop</title></head>
<body>
  <div class="product-card">
    <h1 class="product-title">Premium Widget</h1>
    <span class="price">$29.99</span>
    <span class="brand">WidgetCo</span>
    <a class="product-link" href="/products/widget-1">View Product</a>
    <img class="product-image" src="/images/widget.jpg" alt="Widget" />
    <p class="description">  A high-quality   widget  for all uses.  </p>
    <span class="rating">4.5</span>
    <ul class="features">
      <li>Feature A</li>
      <li>Feature B</li>
      <li>Feature C</li>
    </ul>
  </div>
  <div class="product-card">
    <h1 class="product-title">Budget Widget</h1>
    <span class="price">€9,99</span>
    <a href="https://example.com/page2">Next</a>
    <img src="https://example.com/img2.png" alt="Second" />
  </div>
</body>
</html>"""


class TestDataExtractor(unittest.TestCase):
    """Tests for DataExtractor."""

    def setUp(self) -> None:
        self.extractor = DataExtractor(PRODUCT_HTML)

    # ------------------------------------------------------------------
    # CSS extraction
    # ------------------------------------------------------------------

    def test_extract_by_css_text(self) -> None:
        """Extract text content via a CSS selector."""
        result = self.extractor.extract_by_css("h1.product-title")
        self.assertEqual(result, "Premium Widget")

    def test_extract_by_css_attribute(self) -> None:
        """Extract an HTML attribute via a CSS selector."""
        result = self.extractor.extract_by_css("a.product-link", attribute="href")
        self.assertEqual(result, "/products/widget-1")

    def test_extract_by_css_multiple(self) -> None:
        """Return all matches when multiple=True."""
        results = self.extractor.extract_by_css("h1.product-title", multiple=True)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertIn("Premium Widget", results)
        self.assertIn("Budget Widget", results)

    def test_extract_by_css_missing_selector(self) -> None:
        """Return None when selector matches nothing."""
        result = self.extractor.extract_by_css(".does-not-exist")
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Tag extraction
    # ------------------------------------------------------------------

    def test_extract_by_tag(self) -> None:
        """Extract the first matching HTML tag's text."""
        result = self.extractor.extract_by_tag("title")
        self.assertEqual(result, "Test Shop")

    def test_extract_by_tag_attribute(self) -> None:
        """Extract an attribute from the first matching HTML tag."""
        result = self.extractor.extract_by_tag("img", attribute="src")
        self.assertEqual(result, "/images/widget.jpg")

    def test_extract_by_tag_multiple(self) -> None:
        """Return all matching tag values as a list."""
        results = self.extractor.extract_by_tag("li", multiple=True)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)

    # ------------------------------------------------------------------
    # Link / image extraction
    # ------------------------------------------------------------------

    def test_extract_links(self) -> None:
        """Extract all href values from anchor tags."""
        links = self.extractor.extract_links()
        self.assertIn("/products/widget-1", links)
        self.assertIn("https://example.com/page2", links)

    def test_extract_links_with_base_url(self) -> None:
        """Relative hrefs are resolved when base_url is provided."""
        links = self.extractor.extract_links(base_url="https://myshop.com")
        self.assertIn("https://myshop.com/products/widget-1", links)

    def test_extract_images(self) -> None:
        """Extract all img src values."""
        images = self.extractor.extract_images()
        self.assertIn("/images/widget.jpg", images)
        self.assertIn("https://example.com/img2.png", images)

    def test_extract_images_with_base_url(self) -> None:
        """Relative img srcs are resolved when base_url is provided."""
        images = self.extractor.extract_images(base_url="https://myshop.com")
        self.assertIn("https://myshop.com/images/widget.jpg", images)

    # ------------------------------------------------------------------
    # Regex extraction
    # ------------------------------------------------------------------

    def test_extract_by_regex(self) -> None:
        """Match a regex pattern against the raw HTML."""
        result = self.extractor.extract_by_regex(r"\$[\d.]+")
        self.assertEqual(result, "$29.99")

    def test_extract_by_regex_no_match(self) -> None:
        """Return None when the pattern has no match."""
        result = self.extractor.extract_by_regex(r"XYZZY_NO_MATCH")
        self.assertIsNone(result)

    def test_extract_by_regex_group(self) -> None:
        """Capture a specific group from the regex match."""
        result = self.extractor.extract_by_regex(r"\$([\d.]+)", group=1)
        self.assertEqual(result, "29.99")

    # ------------------------------------------------------------------
    # Text cleaning
    # ------------------------------------------------------------------

    def test_clean_text(self) -> None:
        """Strip and normalise whitespace."""
        result = self.extractor.clean_text("  hello   world  ")
        self.assertEqual(result, "hello world")

    def test_clean_text_empty(self) -> None:
        """Return empty string for empty input."""
        self.assertEqual(self.extractor.clean_text(""), "")

    # ------------------------------------------------------------------
    # Price extraction
    # ------------------------------------------------------------------

    def test_extract_price_dollar(self) -> None:
        """Parse a USD price string."""
        result = self.extractor.extract_price("$29.99")
        self.assertAlmostEqual(result, 29.99)

    def test_extract_price_euro_comma(self) -> None:
        """Parse a European-style price with comma decimal."""
        result = self.extractor.extract_price("€9,99")
        self.assertAlmostEqual(result, 9.99)

    def test_extract_price_thousands(self) -> None:
        """Parse a price with thousands separator."""
        result = self.extractor.extract_price("$1,299.99")
        self.assertAlmostEqual(result, 1299.99)

    def test_extract_price_none(self) -> None:
        """Return None for unparseable input."""
        result = self.extractor.extract_price("N/A")
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Batch extraction
    # ------------------------------------------------------------------

    def test_extract_multiple(self) -> None:
        """extract_multiple returns all requested fields in a single call."""
        spec = {
            "title": {"selector": "h1.product-title", "type": "css", "attribute": "text"},
            "price": {"selector": "span.price", "type": "css", "attribute": "text"},
            "link": {"selector": "a.product-link", "type": "css", "attribute": "href"},
        }
        result = self.extractor.extract_multiple(spec)
        self.assertEqual(result["title"], "Premium Widget")
        self.assertEqual(result["price"], "$29.99")
        self.assertEqual(result["link"], "/products/widget-1")

    def test_extract_multiple_missing_field(self) -> None:
        """Missing selectors produce None, not exceptions."""
        spec = {
            "ghost": {"selector": ".does-not-exist", "type": "css"},
        }
        result = self.extractor.extract_multiple(spec)
        self.assertIsNone(result["ghost"])


if __name__ == "__main__":
    unittest.main()
