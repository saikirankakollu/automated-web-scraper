# API Reference

---

## WebScraper

```
src.scraper.WebScraper
```

Fetches web pages using requests/BeautifulSoup, Selenium, or Scrapy.

### Constructor

```python
WebScraper(config: dict | None = None)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `config` | `dict` | `None` | Optional configuration dict (see [Configuration Guide](CONFIGURATION_GUIDE.md)) |

### Methods

#### `scrape_url(url, method='requests')`

Fetch *url* and return a parsed `BeautifulSoup` object.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `url` | `str` | – | Target URL |
| `method` | `str` | `'requests'` | `'requests'` or `'selenium'` |

**Returns:** `BeautifulSoup | None`

---

#### `scrape_with_selenium(url)`

Fetch *url* using a headless Chrome browser (requires ChromeDriver on PATH).

**Returns:** `BeautifulSoup | None`

---

#### `scrape_with_scrapy(url)`

Run `scrapy fetch` in a subprocess and return raw HTML.

**Returns:** `str | None`

---

#### `close()`

Close the underlying `requests.Session`.

---

## DataExtractor

```
src.extractor.DataExtractor
```

Extracts structured data from an HTML document.

### Constructor

```python
DataExtractor(html_content: str | BeautifulSoup)
```

### Methods

#### `extract_by_css(selector, attribute=None, multiple=False)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `selector` | `str` | – | CSS selector |
| `attribute` | `str \| None` | `None` | HTML attribute to read; `None`/`"text"` returns visible text |
| `multiple` | `bool` | `False` | Return all matches as a list |

**Returns:** `str | None` or `list[str]`

---

#### `extract_by_tag(tag, attribute=None, multiple=False)`

Same signature as `extract_by_css` but takes an HTML tag name instead of a CSS selector.

---

#### `extract_links(base_url=None)`

Extract all `<a href>` values.

| Parameter | Type | Description |
|---|---|---|
| `base_url` | `str \| None` | Resolve relative URLs against this base |

**Returns:** `list[str]`

---

#### `extract_images(base_url=None)`

Extract all `<img src>` values (also checks `data-src`).

**Returns:** `list[str]`

---

#### `extract_by_regex(pattern, group=0)`

Search raw HTML for *pattern* and return the first match.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pattern` | `str` | – | Python regex string |
| `group` | `int` | `0` | Capture group to return |

**Returns:** `str | None`

---

#### `extract_multiple(selectors_dict)`

Batch-extract named fields in a single call.

```python
spec = {
    "name":  {"selector": "h1",       "type": "css",   "attribute": "text"},
    "price": {"selector": ".price",   "type": "css",   "attribute": "text"},
    "sku":   {"selector": r"\d{6}",   "type": "regex"},
}
result = extractor.extract_multiple(spec)
```

**Returns:** `dict[str, Any]`

---

#### `clean_text(text)`

Strip and normalise whitespace. **Returns:** `str`

---

#### `extract_price(text)`

Parse a price string to float. **Returns:** `float | None`

---

## DatabaseManager

```
src.database.DatabaseManager
```

### Constructor

```python
DatabaseManager(
    db_type: str = 'sqlite',
    connection_string: str | None = None,
    db_path: str = 'data/scraper.db',
)
```

### Methods

| Method | Signature | Returns |
|---|---|---|
| `create_tables()` | `() -> None` | – |
| `insert_product(data)` | `(dict) -> int` | Row ID |
| `insert_products_batch(products_list)` | `(list[dict]) -> int` | Record count |
| `get_products(filters=None, limit=100)` | `(dict\|None, int) -> list[dict]` | Product list |
| `log_scrape(domain, status, records_extracted=0, errors=None)` | – | Log row ID |
| `get_scrape_logs(domain=None)` | `(str\|None) -> list[dict]` | Log list |
| `close()` | `() -> None` | – |

---

## ConfigParser

```
src.config_parser.ConfigParser
```

### Methods

| Method | Description |
|---|---|
| `load(filepath)` | Auto-detect format and load config |
| `load_json(filepath)` | Load JSON config |
| `load_yaml(filepath)` | Load YAML config |
| `validate(config)` | Validate required fields; raises `ValueError` |
| `get_default_config()` | Return default config dict |
| `substitute_env_vars(config)` | Replace `${VAR}` with env values |

---

## setup_logger

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

Creates a logger with console and (optionally) rotating file handlers.

---

## Scheduler

```
src.scheduler.Scheduler
```

### Constructor

```python
Scheduler()
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `add_job(func, trigger, job_id=None, **kwargs)` | → `str` | Add a job with any APScheduler trigger |
| `add_cron_job(func, cron_expression, job_id=None)` | → `str` | Add a 5-field cron job |
| `add_interval_job(func, minutes=60, job_id=None)` | → `str` | Add an interval job |
| `start()` | `() -> None` | Start the background scheduler |
| `stop(wait=True)` | `(bool) -> None` | Stop the scheduler |
| `get_jobs()` | `() -> list` | List all scheduled jobs |
| `remove_job(job_id)` | `(str) -> None` | Remove a job by ID |

---

## Utility Functions

```
src.utils
```

| Function | Signature | Description |
|---|---|---|
| `validate_url(url)` | `(str) -> bool` | Validate HTTP/HTTPS URL |
| `normalize_url(url, base_url=None)` | `(str, str\|None) -> str` | Resolve and normalise URL |
| `clean_text(text)` | `(str) -> str` | Strip and normalise whitespace |
| `extract_domain(url)` | `(str) -> str` | Extract domain from URL |
| `export_to_csv(data, filepath)` | `(list[dict], str) -> None` | Write data to CSV |
| `export_to_json(data, filepath)` | `(list[dict], str) -> None` | Write data to JSON |
| `ensure_directory(path)` | `(str) -> None` | Create directory if needed |
| `convert_price(price_str)` | `(str) -> float\|None` | Parse price string to float |
| `slugify(text)` | `(str) -> str` | Create URL-friendly slug |
| `truncate_text(text, max_length=200)` | `(str, int) -> str` | Truncate with ellipsis |
