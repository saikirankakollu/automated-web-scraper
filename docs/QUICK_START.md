# Quick Start

Get your first scrape running in under 5 minutes.

---

## 1. Install

```bash
git clone https://github.com/yourusername/automated-web-scraper.git
cd automated-web-scraper
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2. Run the Built-in Example

The `examples/basic_scrape.py` script scrapes the public demo site
[books.toscrape.com](https://books.toscrape.com) and prints book titles:

```bash
python examples/basic_scrape.py
```

Expected output:

```
Found 20 books on the page:

  A Light in the Attic                              £51.77
  Tipping the Velvet                                £53.74
  Soumission                                        £50.10
  Sharp Objects                                     £47.82
  Sapiens: A Brief History of Humankind             £54.23

Done. Showing first 5 results only.
```

---

## 3. Scrape a URL from Python

```python
from src.scraper import WebScraper
from src.extractor import DataExtractor

scraper = WebScraper({"delay": 1})
soup = scraper.scrape_url("https://books.toscrape.com/")

extractor = DataExtractor(soup)
titles = extractor.extract_by_css("article.product_pod h3 a",
                                   attribute="title",
                                   multiple=True)
for title in titles[:5]:
    print(title)
```

---

## 4. Use a Config File

```python
from src.config_parser import ConfigParser
from src.scraper import WebScraper

parser = ConfigParser()
config = parser.load("config/generic_ecommerce.json")

scraper = WebScraper(config["scraping"])
soup = scraper.scrape_url(config["seed_urls"][0])
```

---

## 5. Save Results to a Database

```python
from src.database import DatabaseManager

db = DatabaseManager()      # uses data/scraper.db by default
db.create_tables()
db.insert_product({
    "name": "Widget Pro",
    "price": 29.99,
    "brand": "Acme",
    "url": "https://example.com/widget",
})
products = db.get_products()
print(products)
db.close()
```

---

## 6. Export to CSV / JSON

```python
from src.utils import export_to_csv, export_to_json

products = [{"name": "Widget", "price": 9.99}]
export_to_csv(products, "exports/products.csv")
export_to_json(products, "exports/products.json")
```

---

## Next Steps

- Read the [Configuration Guide](CONFIGURATION_GUIDE.md) to tailor selectors for your target site.
- Browse [Examples](EXAMPLES.md) for real-world usage patterns.
- See the [API Reference](API_REFERENCE.md) for full method documentation.
- Set up automated runs with the [Scheduler](API_REFERENCE.md#scheduler).
