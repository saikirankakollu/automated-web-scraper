# Configuration Guide

---

## Overview

Configuration files define what to scrape, how to scrape it, and where to
store results.  Both **JSON** and **YAML** formats are supported; choose
whichever you find more readable.

```bash
python -c "
from src.config_parser import ConfigParser
config = ConfigParser().load('config/example_config.yaml')
print(config['name'])
"
```

---

## Top-Level Keys

| Key | Required | Description |
|---|---|---|
| `name` | ✓ | Human-readable name for this scraper |
| `seed_urls` | ✓ | List of starting URLs |
| `extraction` | ✓ | Field extraction specification |
| `scraping` | – | Request behaviour (defaults apply) |
| `pagination` | – | Pagination settings |
| `database` | – | Persistence settings |
| `export` | – | CSV / JSON export settings |
| `logging` | – | Log level and file |

---

## `scraping`

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

### Method Comparison

| Method | JavaScript | Speed | Dependencies |
|---|---|---|---|
| `requests` | ✗ | Fast | requests, beautifulsoup4 |
| `selenium` | ✓ | Slow | selenium, chromedriver |
| `scrapy` | ✗ | Fast | scrapy |

---

## `extraction`

### Single-value extraction

```yaml
extraction:
  fields:
    title:
      selector: "h1.product-title"
      type: css
      attribute: text        # "text" returns visible text; any other value reads the HTML attribute
    product_id:
      selector: "[data-product-id]"
      type: css
      attribute: data-product-id
    price_pattern:
      selector: '\$[\d,]+\.\d{2}'
      type: regex
```

### Multiple-product extraction

```yaml
extraction:
  multiple_products: true
  product_container: ".product-card"   # Each match is extracted independently
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

### Extraction `type` values

| Type | Selector format | Description |
|---|---|---|
| `css` (default) | CSS selector string | Uses BeautifulSoup `select()` |
| `tag` | HTML tag name | Uses BeautifulSoup `find_all()` |
| `regex` | Python regex | Searched against raw HTML |

---

## `pagination`

```yaml
pagination:
  enabled: true
  next_page_selector: "a[rel='next']"   # CSS selector for the "Next" link
  max_pages: 20                          # Safety limit
  page_param: page                       # URL query param (optional)
```

---

## `database`

```yaml
database:
  enabled: true
  type: sqlite          # sqlite | postgresql
  path: data/scraper.db

  # PostgreSQL (use connection_string instead of type/path):
  # connection_string: "postgresql+psycopg2://user:${DB_PASSWORD}@host/dbname"
```

Environment variables in `${VARIABLE}` notation are substituted at load
time, keeping secrets out of version control.

---

## `export`

```yaml
export:
  csv: true
  json: true
  output_dir: exports/
  filename_prefix: my_scraper
```

---

## `logging`

```yaml
logging:
  level: INFO       # DEBUG | INFO | WARNING | ERROR
  file: logs/scraper.log
```

---

## Environment Variable Substitution

Any config value may reference an environment variable:

```yaml
database:
  connection_string: "postgresql+psycopg2://user:${DB_PASSWORD}@${DB_HOST}/scraper"
```

Unset variables remain as literal `${VAR}` strings so missing configuration
is surfaced at runtime.

---

## Best Practices

1. **Start with `generic_ecommerce.json`** and adjust selectors for your target site.
2. **Inspect selectors** with your browser's DevTools → right-click → Copy → Copy selector.
3. **Test with `delay: 0.5`** during development; increase to `2–5` in production to be polite.
4. **Use `multiple_products: true`** for listing pages; `false` for detail pages.
5. **Pin `max_pages`** to a small value while building your scraper.
6. **Store credentials** in environment variables, never in config files committed to git.
