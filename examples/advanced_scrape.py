"""Advanced scraping example – pagination, batch DB insert, CSV/JSON export."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scraper import WebScraper
from src.extractor import DataExtractor
from src.database import DatabaseManager
from src.utils import export_to_csv, export_to_json, ensure_directory, convert_price
from src.logger import setup_logger

logger = setup_logger("advanced_example", log_file="logs/advanced.log")

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 3


def scrape_page(scraper: WebScraper, url: str) -> list:
    """Scrape a single catalogue page and return a list of product dicts."""
    soup = scraper.scrape_url(url)
    if soup is None:
        logger.warning("Could not fetch %s", url)
        return []

    extractor = DataExtractor(soup)
    products = []

    containers = soup.select("article.product_pod")
    for container in containers:
        sub = DataExtractor(container)
        name = sub.extract_by_css("h3 a", attribute="title") or ""
        price_str = sub.extract_by_css(".price_color") or ""
        price = convert_price(price_str)
        relative_url = sub.extract_by_css("h3 a", attribute="href") or ""
        img_src = sub.extract_by_css("img", attribute="src") or ""

        products.append({
            "name": name,
            "price": price,
            "url": BASE_URL + relative_url.replace("../", ""),
            "image_url": "https://books.toscrape.com/" + img_src.replace("../", ""),
        })

    return products


def get_next_page_url(soup, base_url: str) -> str | None:
    """Return the absolute URL of the next page, or None."""
    extractor = DataExtractor(soup)
    rel = extractor.extract_by_css("li.next a", attribute="href")
    if rel:
        return base_url + rel
    return None


def main() -> None:
    """Run a multi-page scrape, store to SQLite, and export CSV + JSON."""
    ensure_directory("logs")
    ensure_directory("exports")

    scraper = WebScraper({"delay": 1, "retry_count": 3})
    db = DatabaseManager(db_path="data/advanced_example.db")
    db.create_tables()

    all_products = []
    current_url = START_URL

    for page_num in range(1, MAX_PAGES + 1):
        logger.info("Scraping page %d: %s", page_num, current_url)
        soup = scraper.scrape_url(current_url)
        if soup is None:
            break

        products = scrape_page(scraper, current_url)
        logger.info("  Found %d products on page %d", len(products), page_num)
        all_products.extend(products)

        next_url = get_next_page_url(soup, BASE_URL)
        if not next_url:
            logger.info("No more pages.")
            break
        current_url = next_url

    if all_products:
        count = db.insert_products_batch(all_products)
        logger.info("Inserted %d records into database.", count)

        export_to_csv(all_products, "exports/books_advanced.csv")
        export_to_json(all_products, "exports/books_advanced.json")
        logger.info("Exported data to exports/books_advanced.csv and .json")

        db.log_scrape(
            domain="books.toscrape.com",
            status="success",
            records_extracted=count,
        )
    else:
        logger.warning("No products were scraped.")
        db.log_scrape(domain="books.toscrape.com", status="failed", records_extracted=0)

    print(f"\nScraped {len(all_products)} books across up to {MAX_PAGES} pages.")
    print("Results saved to exports/books_advanced.csv and exports/books_advanced.json")

    scraper.close()
    db.close()


if __name__ == "__main__":
    main()
