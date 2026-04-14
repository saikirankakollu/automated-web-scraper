"""Basic scraping example – fetch a single URL and print extracted data."""

import sys
import os

# Allow running from the repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scraper import WebScraper
from src.extractor import DataExtractor
from src.logger import setup_logger

logger = setup_logger("basic_example")


def main() -> None:
    """Scrape the Books to Scrape demo site and print the first few titles."""
    url = "https://books.toscrape.com/"

    logger.info("Starting basic scrape of %s", url)

    scraper = WebScraper({"delay": 1, "retry_count": 2})

    soup = scraper.scrape_url(url)
    if soup is None:
        logger.error("Failed to fetch %s", url)
        return

    extractor = DataExtractor(soup)

    # Extract all book titles and prices from the listing page
    spec = {
        "title": {
            "selector": "article.product_pod h3 a",
            "type": "css",
            "attribute": "title",
            "multiple": True,
        },
        "price": {
            "selector": "article.product_pod .price_color",
            "type": "css",
            "attribute": "text",
            "multiple": True,
        },
    }

    data = extractor.extract_multiple(spec)
    titles: list = data.get("title") or []
    prices: list = data.get("price") or []

    print(f"\nFound {len(titles)} books on the page:\n")
    for title, price in zip(titles[:5], prices[:5]):
        print(f"  {title:<50} {price}")

    print("\nDone. Showing first 5 results only.")
    scraper.close()


if __name__ == "__main__":
    main()
