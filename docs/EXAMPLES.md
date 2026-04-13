# Examples

---

## Basic Single-URL Scrape

```python
from src.scraper import WebScraper
from src.extractor import DataExtractor

scraper = WebScraper({"delay": 1})
soup = scraper.scrape_url("https://books.toscrape.com/")

extractor = DataExtractor(soup)
titles = extractor.extract_by_css(
    "article.product_pod h3 a",
    attribute="title",
    multiple=True,
)
print(titles[:5])
scraper.close()
```

---

## Multi-Page E-commerce Scrape

```python
from src.scraper import WebScraper
from src.extractor import DataExtractor
from src.database import DatabaseManager

scraper = WebScraper({"delay": 2, "retry_count": 3})
db = DatabaseManager()
db.create_tables()

url = "https://books.toscrape.com/catalogue/page-1.html"
for page in range(1, 6):
    soup = scraper.scrape_url(url)
    if soup is None:
        break

    for article in soup.select("article.product_pod"):
        sub = DataExtractor(article)
        db.insert_product({
            "name": sub.extract_by_css("h3 a", attribute="title"),
            "price": sub.extract_price(sub.extract_by_css(".price_color") or ""),
        })

    next_link = DataExtractor(soup).extract_by_css("li.next a", attribute="href")
    if not next_link:
        break
    url = "https://books.toscrape.com/catalogue/" + next_link

db.close()
scraper.close()
```

---

## Load and Validate a Config File

```python
from src.config_parser import ConfigParser

parser = ConfigParser()
config = parser.load("config/example_config.yaml")
parser.validate(config)

print(config["name"])
print(config["seed_urls"])
```

---

## Extract Multiple Fields at Once

```python
from src.extractor import DataExtractor

html = """
<div class="product">
  <h1 class="title">Widget Pro</h1>
  <span class="price">$49.99</span>
  <a href="/products/widget-pro">Buy</a>
</div>
"""

extractor = DataExtractor(html)
data = extractor.extract_multiple({
    "name":  {"selector": "h1.title",   "type": "css", "attribute": "text"},
    "price": {"selector": "span.price", "type": "css", "attribute": "text"},
    "url":   {"selector": "a",          "type": "css", "attribute": "href"},
})
print(data)
# {'name': 'Widget Pro', 'price': '$49.99', 'url': '/products/widget-pro'}
```

---

## Export Scraped Data

```python
from src.utils import export_to_csv, export_to_json

products = [
    {"name": "Widget A", "price": 9.99, "brand": "Acme"},
    {"name": "Widget B", "price": 19.99, "brand": "Acme"},
]

export_to_csv(products, "exports/widgets.csv")
export_to_json(products, "exports/widgets.json")
```

---

## Selenium Scraping (JavaScript-Heavy Sites)

```python
from src.scraper import WebScraper

# Selenium requires chromedriver on PATH
scraper = WebScraper({"delay": 3})
soup = scraper.scrape_with_selenium("https://example.com/js-heavy-page")
if soup:
    title = soup.find("title")
    print(title.get_text() if title else "(no title)")
scraper.close()
```

---

## Scheduled Periodic Scraping

```python
import time
from src.scheduler import Scheduler
from src.scraper import WebScraper

def my_scrape_job():
    s = WebScraper({"delay": 1})
    soup = s.scrape_url("https://books.toscrape.com/")
    if soup:
        print(f"Page title: {soup.find('title').get_text()}")
    s.close()

scheduler = Scheduler()
scheduler.add_interval_job(my_scrape_job, minutes=30, job_id="demo")
scheduler.start()

try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    scheduler.stop()
```

---

## PostgreSQL Backend

```python
from src.database import DatabaseManager

db = DatabaseManager(
    connection_string="postgresql+psycopg2://user:password@localhost/scraper"
)
db.create_tables()
db.insert_product({"name": "Widget", "price": 9.99})
db.close()
```

---

## Error Handling Pattern

```python
from src.scraper import WebScraper
from src.database import DatabaseManager

scraper = WebScraper({"retry_count": 3})
db = DatabaseManager()
db.create_tables()

url = "https://example.com/products"
try:
    soup = scraper.scrape_url(url)
    if soup is None:
        raise RuntimeError(f"Failed to fetch {url}")
    # … extraction logic …
    db.log_scrape("example.com", "success", records_extracted=10)
except Exception as exc:
    db.log_scrape("example.com", "failed", errors=str(exc))
    raise
finally:
    scraper.close()
    db.close()
```

---

## Regex-Based Extraction

```python
from src.extractor import DataExtractor

html = '<script>var productId = 987654;</script>'
extractor = DataExtractor(html)

product_id = extractor.extract_by_regex(r'productId\s*=\s*(\d+)', group=1)
print(product_id)  # "987654"
```
