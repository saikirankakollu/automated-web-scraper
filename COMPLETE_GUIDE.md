# Automated Web Scraper — Complete Guide

> A production-ready, multi-library Python web scraper for e-commerce data extraction  
> with flexible configuration, scheduled execution, and multiple export formats.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Project Structure](#3-project-structure)
4. [Installation](#4-installation)
5. [Quick Start](#5-quick-start)
6. [Configuration Guide](#6-configuration-guide)
7. [API Reference](#7-api-reference)
8. [Examples](#8-examples)
9. [Example Scripts](#9-example-scripts)
10. [Configuration File Templates](#10-configuration-file-templates)
11. [Running Tests](#11-running-tests)
12. [Troubleshooting](#12-troubleshooting)
13. [Contributing](#13-contributing)
14. [License](#14-license)

---

## 1. Project Overview

**automated-web-scraper** is a configuration-driven Python package that extracts
product data (names, prices, brands, images, ratings, stock status) from any
e-commerce website.  It supports three scraping backends, two database engines,
two configuration formats, built-in scheduling, and CSV/JSON export — all
controlled by a single config file without touching Python code.

---

## 2. Features

| Category | Details |
|---|---|
| **Scraping backends** | `requests` + BeautifulSoup, Selenium (headless Chrome), Scrapy |
| **Extraction methods** | CSS selectors, HTML tag search, regex patterns, links (`href`), images (`src`) |
| **Configuration** | JSON and YAML config files with `${ENV_VAR}` substitution |
| **Databases** | SQLite (default) and PostgreSQL via SQLAlchemy |
| **Scheduling** | Cron and interval jobs via APScheduler |
| **Export** | CSV and JSON helpers |
| **Reliability** | Exponential back-off retries, proxy rotation, user-agent rotation |
| **Observability** | Rotating file + console logging, per-session scrape logs in DB |
| **Type safety** | Full Python type hints |
| **Tests** | 38 unittest cases covering extractor and database layers |

---

## 3. Project Structure

```
automated-web-scraper/
├── config/                        # JSON and YAML configuration templates
│   ├── generic_ecommerce.json     # Ready-to-use e-commerce template
│   ├── example_config.json        # Annotated JSON example
│   ├── example_config.yaml        # YAML equivalent
│   └── domains_config.yaml        # Multi-domain configuration
│
├── docs/                          # Individual documentation pages
│   ├── INSTALLATION.md
│   ├── QUICK_START.md
│   ├── CONFIGURATION_GUIDE.md
│   ├── API_REFERENCE.md
│   ├── EXAMPLES.md
│   └── TROUBLESHOOTING.md
│
├── examples/                      # Runnable example scripts
│   ├── basic_scrape.py            # Single-page scrape
│   ├── advanced_scrape.py         # Pagination + DB + export
│   └── scheduler_example.py      # Periodic scheduled scraping
│
├── src/                           # Library source code
│   ├── __init__.py
│   ├── scraper.py                 # WebScraper – multi-backend fetcher
│   ├── extractor.py               # DataExtractor – CSS / tag / regex extraction
│   ├── database.py                # DatabaseManager – SQLite & PostgreSQL
│   ├── config_parser.py           # ConfigParser – JSON/YAML loader
│   ├── scheduler.py               # Scheduler – APScheduler wrapper
│   ├── utils.py                   # Utility functions
│   └── logger.py                  # Logging setup
│
├── tests/                         # Unit tests
│   ├── __init__.py
│   ├── test_extractor.py          # 19 DataExtractor tests
│   └── test_database.py           # 19 DatabaseManager tests
│
├── data/                          # SQLite database files (git-ignored)
│   └── .gitkeep
├── exports/                       # Exported CSV/JSON files (git-ignored)
│   └── .gitkeep
│
├── COMPLETE_GUIDE.md              # ← You are here
├── README.md
├── requirements.txt
└── setup.py
```

---

## 4. Installation

### Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.8 |
| pip | ≥ 21.0 |

### Step 1 — Clone the Repository

```bash
git clone https://github.com/saikirankakollu/automated-web-scraper.git
cd automated-web-scraper
```

### Step 2 — Create and Activate a Virtual Environment

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Step 3 — Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependencies**

```
beautifulsoup4>=4.11.0
requests>=2.28.0
scrapy>=2.8.0
selenium>=4.10.0
pyyaml>=6.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
apscheduler>=3.10.0
python-dateutil>=2.8.0
lxml>=4.9.0
```

### Optional — Install as a Package

```bash
pip install -e .
```

This makes the `webscraper` CLI entry point available within the virtual environment.

### Step 4 — Install WebDriver (Selenium Only)

If you plan to use the Selenium backend you need Google Chrome and a matching ChromeDriver.

**Automatic (recommended)**
```bash
pip install webdriver-manager
```

Then update `scrape_with_selenium` in `src/scraper.py`:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
```

**Manual** — download ChromeDriver from <https://chromedriver.chromium.org/downloads>
matching your Chrome version and place the binary on your `PATH`.

### Step 5 — Database Initialisation

SQLite is created automatically on first use.  For **PostgreSQL**, set the
connection string as an environment variable:

```bash
export DB_CONNECTION_STRING="postgresql+psycopg2://user:pass@localhost/scraper"
```

### Step 6 — Verify Installation

```bash
python -c "from src import WebScraper, DataExtractor; print('OK')"
python -m pytest tests/ -v
```

### Platform Notes

| Platform | Notes |
|---|---|
| **macOS (Apple Silicon)** | `pip install psycopg2 --no-binary psycopg2` if binary fails |
| **Windows** | `lxml` may need the Visual C++ Build Tools |
| **Linux** | `sudo apt-get install libxml2-dev libxslt1-dev libpq-dev python3-dev` |

---

## 5. Quick Start

### Run the Built-in Example

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

### Scrape a URL in Python

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
scraper.close()
```

### Use a Config File

```python
from src.config_parser import ConfigParser
from src.scraper import WebScraper

config = ConfigParser().load("config/generic_ecommerce.json")
scraper = WebScraper(config["scraping"])
soup = scraper.scrape_url(config["seed_urls"][0])
```

### Save Results to a Database

```python
from src.database import DatabaseManager

db = DatabaseManager()   # uses data/scraper.db by default
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

### Export to CSV / JSON

```python
from src.utils import export_to_csv, export_to_json

products = [{"name": "Widget", "price": 9.99}]
export_to_csv(products, "exports/products.csv")
export_to_json(products, "exports/products.json")
```

---

## 6. Configuration Guide

### Overview

Configuration files define *what* to scrape, *how* to scrape it, and *where*
to store results.  Both **JSON** and **YAML** formats are supported.

```python
from src.config_parser import ConfigParser
config = ConfigParser().load("config/example_config.yaml")
print(config["name"])
```

### Top-Level Keys

| Key | Required | Description |
|---|---|---|
| `name` | ✓ | Human-readable name for this scraper |
| `seed_urls` | ✓ | List of starting URLs |
| `extraction` | ✓ | Field extraction specification |
| `scraping` | – | Request behaviour (defaults apply) |
| `pagination` | – | Pagination settings |
| `database` | – | Persistence settings |
| `export` | – | CSV / JSON export settings |
| `logging` | – | Log level and output file |

---

### `scraping`

```yaml
scraping:
  method: requests        # requests | selenium | scrapy
  delay: 2                # seconds between page requests
  retry_count: 3          # max retries on failure
  timeout: 30             # HTTP timeout (seconds)
  user_agent_rotation: true
  proxies:
    - "http://proxy1.example.com:8080"
    - "http://proxy2.example.com:8080"
  headers:
    X-Custom-Header: "value"
  cookies:
    session_id: "abc123"
```

| Method | JavaScript | Speed | Dependencies |
|---|---|---|---|
| `requests` | ✗ | Fast | requests, beautifulsoup4 |
| `selenium` | ✓ | Slow | selenium, chromedriver |
| `scrapy` | ✗ | Fast | scrapy |

---

### `extraction`

#### Single-value fields

```yaml
extraction:
  fields:
    title:
      selector: "h1.product-title"
      type: css
      attribute: text          # "text" = visible text; any other value reads the HTML attribute
    product_id:
      selector: "[data-product-id]"
      type: css
      attribute: data-product-id
    price_pattern:
      selector: '\$[\d,]+\.\d{2}'
      type: regex
```

#### Multiple-product extraction (listing pages)

```yaml
extraction:
  multiple_products: true
  product_container: ".product-card"
  fields:
    name:
      selector: "h2"
      type: css
      attribute: text
    price:
      selector: ".price"
      type: css
      attribute: text
```

#### Extraction `type` values

| Type | Selector format | Description |
|---|---|---|
| `css` (default) | CSS selector string | Uses BeautifulSoup `select()` |
| `tag` | HTML tag name | Uses BeautifulSoup `find_all()` |
| `regex` | Python regex | Searched against raw HTML |

---

### `pagination`

```yaml
pagination:
  enabled: true
  next_page_selector: "a[rel='next']"   # CSS selector for the "Next" link
  max_pages: 20                          # Safety limit
  page_param: page                       # URL query param (optional)
```

---

### `database`

```yaml
database:
  enabled: true
  type: sqlite          # sqlite | postgresql
  path: data/scraper.db

  # PostgreSQL — use connection_string with env vars to keep secrets safe:
  # connection_string: "postgresql+psycopg2://user:${DB_PASSWORD}@host/dbname"
```

---

### `export`

```yaml
export:
  csv: true
  json: true
  output_dir: exports/
  filename_prefix: my_scraper
```

---

### `logging`

```yaml
logging:
  level: INFO       # DEBUG | INFO | WARNING | ERROR
  file: logs/scraper.log
```

---

### Environment Variable Substitution

Any config value may reference an environment variable using `${VAR}` notation:

```yaml
database:
  connection_string: "postgresql+psycopg2://user:${DB_PASSWORD}@${DB_HOST}/scraper"
```

Unset variables remain as literal `${VAR}` strings, surfacing missing
configuration at runtime rather than silently failing.

---

### Best Practices

1. **Start with `generic_ecommerce.json`** and adjust selectors for your target site.
2. **Inspect selectors** with browser DevTools → right-click element → Copy → Copy selector.
3. **Test with `delay: 0.5`** during development; increase to `2–5` in production.
4. **Use `multiple_products: true`** for listing pages; `false` for detail pages.
5. **Pin `max_pages`** to a small value while building your scraper.
6. **Store credentials** in environment variables, never in config files committed to git.

---

## 7. API Reference

### WebScraper

```
src.scraper.WebScraper
```

Fetches web pages using requests/BeautifulSoup, Selenium, or Scrapy.

#### Constructor

```python
WebScraper(config: dict | None = None)
```

#### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `scrape_url` | `(url, method='requests')` | `BeautifulSoup \| None` | Fetch *url* and return parsed HTML |
| `scrape_with_selenium` | `(url)` | `BeautifulSoup \| None` | Headless Chrome fetch |
| `scrape_with_scrapy` | `(url)` | `str \| None` | Scrapy subprocess fetch, returns raw HTML |
| `close` | `()` | `None` | Close the underlying `requests.Session` |

---

### DataExtractor

```
src.extractor.DataExtractor
```

Extracts structured data from an HTML document.

#### Constructor

```python
DataExtractor(html_content: str | BeautifulSoup)
```

#### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `extract_by_css` | `(selector, attribute=None, multiple=False)` | `str \| list \| None` | CSS selector extraction |
| `extract_by_tag` | `(tag, attribute=None, multiple=False)` | `str \| list \| None` | HTML tag extraction |
| `extract_links` | `(base_url=None)` | `list[str]` | All `<a href>` values |
| `extract_images` | `(base_url=None)` | `list[str]` | All `<img src>` / `data-src` values |
| `extract_by_regex` | `(pattern, group=0)` | `str \| None` | First regex match in raw HTML |
| `extract_multiple` | `(selectors_dict)` | `dict[str, Any]` | Batch-extract named fields |
| `clean_text` | `(text)` | `str` | Strip and normalise whitespace |
| `extract_price` | `(text)` | `float \| None` | Parse price string to float |

**`extract_multiple` spec format:**
```python
{
  "field_name": {
    "selector": "...",     # CSS selector, tag name, or regex
    "type": "css",         # css | tag | regex
    "attribute": "text",   # attribute name or "text"
    "multiple": False,     # return list if True
  }
}
```

---

### DatabaseManager

```
src.database.DatabaseManager
```

#### Constructor

```python
DatabaseManager(
    db_type: str = 'sqlite',
    connection_string: str | None = None,
    db_path: str = 'data/scraper.db',
)
```

#### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `create_tables` | `()` | `None` | Create `products` and `scrape_logs` tables |
| `insert_product` | `(data: dict)` | `int` | Insert one product, return row ID |
| `insert_products_batch` | `(products_list: list)` | `int` | Batch insert, return count |
| `get_products` | `(filters=None, limit=100)` | `list[dict]` | Query products |
| `log_scrape` | `(domain, status, records_extracted=0, errors=None)` | `int` | Log a scrape session |
| `get_scrape_logs` | `(domain=None)` | `list[dict]` | Retrieve logs (newest first) |
| `close` | `()` | `None` | Close the database connection |

**Products table schema:** `id`, `name`, `price`, `brand`, `url`, `image_url`, `rating`, `stock`, `created_at`, `updated_at`

**Scrape logs schema:** `id`, `domain`, `timestamp`, `status`, `records_extracted`, `errors`

---

### ConfigParser

```
src.config_parser.ConfigParser
```

#### Methods

| Method | Description |
|---|---|
| `load(filepath)` | Auto-detect format (JSON/YAML) and load |
| `load_json(filepath)` | Load JSON config |
| `load_yaml(filepath)` | Load YAML config |
| `validate(config)` | Validate required fields; raises `ValueError` on failure |
| `get_default_config()` | Return default config dict |
| `substitute_env_vars(config)` | Replace all `${VAR}` patterns with env values |

---

### setup_logger

```
src.logger.setup_logger
```

```python
setup_logger(
    name: str,
    log_file: str | None = None,
    level: int = logging.INFO,
) -> logging.Logger
```

Creates a logger with a console handler and (optionally) a rotating file
handler (10 MB max, 5 backups).  Format: `timestamp | LEVEL | module | message`.

---

### Scheduler

```
src.scheduler.Scheduler
```

#### Constructor

```python
Scheduler()
```

#### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_job` | `(func, trigger, job_id=None, **kwargs)` | `str` | Add a job with any APScheduler trigger |
| `add_cron_job` | `(func, cron_expression, job_id=None)` | `str` | Add a 5-field cron job |
| `add_interval_job` | `(func, minutes=60, job_id=None)` | `str` | Add an interval job |
| `start` | `()` | `None` | Start the background scheduler |
| `stop` | `(wait=True)` | `None` | Stop the scheduler |
| `get_jobs` | `()` | `list` | List all scheduled jobs |
| `remove_job` | `(job_id)` | `None` | Remove a job by ID |

---

### Utility Functions (`src.utils`)

| Function | Signature | Description |
|---|---|---|
| `validate_url` | `(url: str) -> bool` | Validate HTTP/HTTPS URL |
| `normalize_url` | `(url, base_url=None) -> str` | Resolve and normalise URL |
| `clean_text` | `(text: str) -> str` | Strip and normalise whitespace |
| `extract_domain` | `(url: str) -> str` | Extract domain from URL |
| `export_to_csv` | `(data, filepath) -> None` | Write list of dicts to CSV |
| `export_to_json` | `(data, filepath) -> None` | Write list of dicts to JSON |
| `ensure_directory` | `(path: str) -> None` | Create directory if missing |
| `convert_price` | `(price_str: str) -> float \| None` | Parse price string to float |
| `slugify` | `(text: str) -> str` | Create URL-friendly slug |
| `truncate_text` | `(text, max_length=200) -> str` | Truncate with ellipsis |

---

## 8. Examples

### Basic Single-URL Scrape

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

### Multi-Page E-commerce Scrape

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
            "name":  sub.extract_by_css("h3 a", attribute="title"),
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

### Load and Validate a Config File

```python
from src.config_parser import ConfigParser

parser = ConfigParser()
config = parser.load("config/example_config.yaml")
parser.validate(config)

print(config["name"])
print(config["seed_urls"])
```

---

### Extract Multiple Fields at Once

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

### Export Scraped Data

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

### Selenium Scraping (JavaScript-Heavy Sites)

```python
from src.scraper import WebScraper

scraper = WebScraper({"delay": 3})
soup = scraper.scrape_with_selenium("https://example.com/js-heavy-page")
if soup:
    title = soup.find("title")
    print(title.get_text() if title else "(no title)")
scraper.close()
```

---

### Scheduled Periodic Scraping

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

### PostgreSQL Backend

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

### Error Handling Pattern

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

### Regex-Based Extraction

```python
from src.extractor import DataExtractor

html = '<script>var productId = 987654;</script>'
extractor = DataExtractor(html)

product_id = extractor.extract_by_regex(r'productId\s*=\s*(\d+)', group=1)
print(product_id)  # "987654"
```

---

## 9. Example Scripts

### `examples/basic_scrape.py`

```python
"""Basic scraping example – fetch a single URL and print extracted data."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scraper import WebScraper
from src.extractor import DataExtractor
from src.logger import setup_logger

logger = setup_logger("basic_example")


def main() -> None:
    url = "https://books.toscrape.com/"
    logger.info("Starting basic scrape of %s", url)

    scraper = WebScraper({"delay": 1, "retry_count": 2})
    soup = scraper.scrape_url(url)
    if soup is None:
        logger.error("Failed to fetch %s", url)
        return

    extractor = DataExtractor(soup)
    spec = {
        "title": {"selector": "article.product_pod h3 a", "type": "css",
                  "attribute": "title", "multiple": True},
        "price": {"selector": "article.product_pod .price_color", "type": "css",
                  "attribute": "text", "multiple": True},
    }
    data = extractor.extract_multiple(spec)
    titles = data.get("title") or []
    prices = data.get("price") or []

    print(f"\nFound {len(titles)} books on the page:\n")
    for title, price in zip(titles[:5], prices[:5]):
        print(f"  {title:<50} {price}")
    print("\nDone. Showing first 5 results only.")
    scraper.close()


if __name__ == "__main__":
    main()
```

**Run it:**
```bash
python examples/basic_scrape.py
```

---

### `examples/advanced_scrape.py`

Multi-page scrape with DB insert and CSV/JSON export.

**Run it:**
```bash
python examples/advanced_scrape.py
```

Output files: `exports/books_advanced.csv`, `exports/books_advanced.json`

---

### `examples/scheduler_example.py`

Runs the scraper every 2 minutes and also schedules a daily cron job at 06:00.

**Run it:**
```bash
python examples/scheduler_example.py
# Press Ctrl+C to stop
```

---

## 10. Configuration File Templates

### `config/generic_ecommerce.json`

```json
{
  "name": "Generic E-commerce Scraper",
  "seed_urls": ["https://example-shop.com/products"],
  "scraping": {
    "method": "requests",
    "delay": 2,
    "retry_count": 3,
    "timeout": 30,
    "user_agent_rotation": true,
    "proxies": []
  },
  "extraction": {
    "fields": {
      "name":         {"selector": "h1.product-title, .product-name, [itemprop='name']",  "type": "css", "attribute": "text"},
      "price":        {"selector": ".price, .product-price, [itemprop='price']",           "type": "css", "attribute": "text"},
      "brand":        {"selector": ".brand, .product-brand, [itemprop='brand']",           "type": "css", "attribute": "text"},
      "url":          {"selector": "a.product-link",                                        "type": "css", "attribute": "href"},
      "image_url":    {"selector": ".product-image img, .product-photo img",               "type": "css", "attribute": "src"},
      "stock":        {"selector": ".stock-status, .availability",                          "type": "css", "attribute": "text"},
      "rating":       {"selector": ".rating, .star-rating",                                 "type": "css", "attribute": "text"},
      "review_count": {"selector": ".review-count, .num-reviews",                           "type": "css", "attribute": "text"}
    },
    "multiple_products": true,
    "product_container": ".product-item, .product-card, li.product"
  },
  "pagination": {
    "enabled": true,
    "next_page_selector": "a.next, .pagination .next a, a[rel='next']",
    "max_pages": 10
  },
  "database": {
    "enabled": true,
    "type": "sqlite",
    "path": "data/products.db"
  },
  "export": {
    "csv": true,
    "json": true,
    "output_dir": "exports/"
  }
}
```

---

### `config/example_config.yaml`

```yaml
name: Example YAML Scraper
seed_urls:
  - https://example.com/shop/laptops
  - https://example.com/shop/phones

scraping:
  method: requests
  delay: 2.5
  retry_count: 3
  timeout: 30
  user_agent_rotation: true
  proxies: []

extraction:
  product_container: ".product-card"
  multiple_products: true
  fields:
    name:       {selector: "h2.product-title",  type: css, attribute: text,      required: true}
    price:      {selector: "span.price",         type: css, attribute: text,      required: true}
    brand:      {selector: ".brand-name",        type: css, attribute: text}
    url:        {selector: "a.product-link",     type: css, attribute: href}
    image_url:  {selector: "img.product-image",  type: css, attribute: src}
    rating:     {selector: "span.rating-value",  type: css, attribute: text}
    stock:      {selector: ".availability",      type: css, attribute: text}

pagination:
  enabled: true
  next_page_selector: "a[rel='next']"
  max_pages: 20

database:
  enabled: true
  type: sqlite
  path: data/example.db

export:
  csv: true
  json: true
  output_dir: exports/
  filename_prefix: products

logging:
  level: INFO
  file: logs/scraper.log
```

---

## 11. Running Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

The test suite contains **38 tests** across two modules:

| Module | Tests | What is covered |
|---|---|---|
| `tests/test_extractor.py` | 19 | CSS extraction, tag extraction, links, images, regex, price parsing, `extract_multiple`, text cleaning |
| `tests/test_database.py` | 19 | Table creation, product insert, batch insert, filters, scrape logging, log ordering, schema fields |

---

## 12. Troubleshooting

### Installation Issues

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'lxml'` | `pip install lxml`; on Linux also `sudo apt-get install libxml2-dev libxslt1-dev` |
| `ModuleNotFoundError: No module named 'yaml'` | `pip install pyyaml` |
| `psycopg2.OperationalError` | Confirm PostgreSQL is running (`pg_isready`) and credentials are correct |
| `scrapy: command not found` | Activate your virtual environment and run `pip install scrapy` |
| Import errors after `pip install -e .` | Re-activate the virtual environment |

---

### Scraping Issues

| Problem | Solution |
|---|---|
| `403 Forbidden` | Enable `user_agent_rotation: true`, add a `Referer` header, increase `delay`, use a proxy |
| `429 Too Many Requests` | Increase `delay` to 10–30 s; retry logic will back off automatically |
| Empty / `None` from `scrape_url` | Verify URL in browser; if JS-rendered switch to `method: selenium` |
| `WebDriverException: chromedriver not found` | Put `chromedriver` on `PATH` or install `webdriver-manager` |

---

### Extraction Issues

| Problem | Solution |
|---|---|
| CSS selector returns `None` | Verify selector in DevTools console: `document.querySelectorAll('your.selector')` |
| Price extraction returns `None` | Pass raw text to `extract_price()`; use `extract_by_regex(r'[\d,\.]+')` as fallback |
| Content inside `<iframe>` unreachable | iframes are not accessible with CSS selectors; use Selenium to switch frames |

---

### Database Issues

| Problem | Solution |
|---|---|
| `OperationalError: no such table: products` | Call `db.create_tables()` before inserting |
| Data not persisted | Do not use `:memory:` for production; use a file path |

---

### Scheduler Issues

| Problem | Solution |
|---|---|
| Jobs not running | Ensure `scheduler.start()` was called and the main thread is alive |
| `RuntimeError: Scheduler is already running` | Guard: `if not scheduler._scheduler.running: scheduler.start()` |

---

### Performance Tips

| Tip | Impact |
|---|---|
| Use `insert_products_batch()` instead of looping `insert_product()` | High |
| Reuse one `WebScraper` instance across all pages | Medium |
| Set `delay` to the minimum the target site tolerates | Medium |
| Use PostgreSQL for concurrent / high-volume workloads | High |
| Profile: `python -m cProfile your_script.py` | – |

---

### FAQ

**Q: Can I scrape sites that require login?**  
Pass session cookies via the `cookies` config key, or manipulate `scraper._session.cookies` directly.

**Q: How do I handle CAPTCHAs?**  
The scraper does not solve CAPTCHAs automatically.  Use a third-party solving service or obtain a session cookie manually.

**Q: Is scraping legal?**  
Always check the site's `robots.txt` and Terms of Service before scraping.  The tool itself is neutral; responsibility lies with the operator.

**Q: Can I run multiple scrapers in parallel?**  
Create separate `WebScraper` and `DatabaseManager` instances per thread/process.  Use PostgreSQL for high-concurrency workloads (SQLite only supports one writer at a time).

---

### Known Limitations

- Scrapy integration runs via subprocess and does not share the session or cookies with the `requests` backend.
- Selenium support requires Chrome + ChromeDriver; headless Firefox is not currently supported out of the box.
- APScheduler's `BackgroundScheduler` runs as a daemon thread and will not prevent the process from exiting if the main thread ends.

---

## 13. Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Make your changes with tests.
4. Ensure all tests pass: `python -m pytest tests/ -v`.
5. Follow PEP 8 and include docstrings with type hints for all new code.
6. Open a pull request.

---

## 14. License

MIT License — see [LICENSE](LICENSE) for details.
