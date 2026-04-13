# Automated Web Scraper

A production-ready, multi-library Python web scraper with flexible configuration, scheduled execution, and multiple export formats.

---

## Features

- **Multiple scraping backends** – requests/BeautifulSoup, Selenium (headless Chrome), and Scrapy
- **Intelligent retry logic** – exponential back-off on failures with configurable retry count
- **User-agent rotation** – built-in pool of realistic browser user-agents
- **Proxy support** – round-robin proxy rotation
- **Flexible extraction** – CSS selectors, HTML tag search, and regex patterns
- **Batch extraction** – extract multiple named fields in a single call
- **SQLite & PostgreSQL** – pluggable database backend via SQLAlchemy
- **Scheduled scraping** – cron and interval jobs via APScheduler
- **Data export** – CSV and JSON export helpers
- **Config-driven** – JSON and YAML config files with environment variable substitution
- **Fully typed** – Python type hints throughout
- **Comprehensive tests** – unittest suite for extractor and database layers

---

## Quick Start

```bash
# 1. Clone and set up
git clone https://github.com/yourusername/automated-web-scraper.git
cd automated-web-scraper
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the built-in example
python examples/basic_scrape.py
```

---

## Basic Usage

```python
from src.scraper import WebScraper
from src.extractor import DataExtractor
from src.database import DatabaseManager

# Fetch a page
scraper = WebScraper({"delay": 1, "retry_count": 3})
soup = scraper.scrape_url("https://books.toscrape.com/")

# Extract data
extractor = DataExtractor(soup)
titles = extractor.extract_by_css("article.product_pod h3 a",
                                   attribute="title", multiple=True)

# Store results
db = DatabaseManager()
db.create_tables()
for title in titles:
    db.insert_product({"name": title})

db.close()
scraper.close()
```

---

## Configuration

Point the scraper at any site by creating a YAML config:

```yaml
name: My Shop Scraper
seed_urls:
  - https://myshop.example.com/products
scraping:
  method: requests
  delay: 2
  retry_count: 3
extraction:
  product_container: ".product-card"
  multiple_products: true
  fields:
    name:
      selector: "h2.title"
      type: css
      attribute: text
    price:
      selector: ".price"
      type: css
      attribute: text
```

Ready-made templates are in the `config/` directory.

---

## Project Structure

```
automated-web-scraper/
├── config/                  # JSON and YAML configuration templates
├── docs/                    # Detailed documentation
├── examples/                # Runnable example scripts
├── src/                     # Library source code
│   ├── scraper.py           # WebScraper – multi-backend fetcher
│   ├── extractor.py         # DataExtractor – CSS / tag / regex extraction
│   ├── database.py          # DatabaseManager – SQLite & PostgreSQL
│   ├── config_parser.py     # ConfigParser – JSON/YAML loader
│   ├── scheduler.py         # Scheduler – APScheduler wrapper
│   ├── utils.py             # Utility functions
│   └── logger.py            # Logging setup
├── tests/                   # Unit tests
├── data/                    # SQLite database files (git-ignored)
├── exports/                 # Exported CSV/JSON files (git-ignored)
└── requirements.txt
```

---

## Documentation

| Document | Description |
|---|---|
| [Installation Guide](docs/INSTALLATION.md) | Step-by-step setup for all platforms |
| [Quick Start](docs/QUICK_START.md) | Get scraping in 5 minutes |
| [Configuration Guide](docs/CONFIGURATION_GUIDE.md) | All config options explained |
| [API Reference](docs/API_REFERENCE.md) | Full class and method documentation |
| [Examples](docs/EXAMPLES.md) | Real-world usage patterns |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |

---

## Running Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Make your changes with tests.
4. Ensure `python -m pytest tests/ -v` passes.
5. Open a pull request.

Please follow PEP 8 and include docstrings with type hints for any new code.

---

## License

MIT License – see [LICENSE](LICENSE) for details.
