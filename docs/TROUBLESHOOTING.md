# Troubleshooting

---

## Installation Issues

### `ModuleNotFoundError: No module named 'lxml'`

```bash
pip install lxml
```

On Linux you may also need the system library:

```bash
sudo apt-get install libxml2-dev libxslt1-dev   # Debian/Ubuntu
sudo dnf install libxml2-devel libxslt-devel     # Fedora/RHEL
```

---

### `ModuleNotFoundError: No module named 'yaml'`

```bash
pip install pyyaml
```

---

### `psycopg2.OperationalError`

1. Ensure PostgreSQL is running: `pg_isready`
2. Check your connection string credentials.
3. On macOS/Linux you may need: `pip install psycopg2` (compiled) instead of `psycopg2-binary`.

---

## Scraping Issues

### Receiving `403 Forbidden`

- Enable user-agent rotation: `user_agent_rotation: true`
- Add a realistic `Referer` header.
- Increase `delay` to 3–5 seconds.
- Use a proxy if the IP is blocked.

### Receiving `429 Too Many Requests`

- Increase `delay` significantly (10–30 s).
- The retry logic uses exponential back-off and will retry `429` automatically.
- Consider adding proxy rotation.

### Empty / `None` Result from `scrape_url`

1. Check the URL is reachable in a browser.
2. Add `logger.debug` to inspect the raw HTML.
3. If the site requires JavaScript, switch to `method: selenium`.

### Selenium `WebDriverException: chromedriver not found`

- Ensure `chromedriver` is on `PATH`.
- Install [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager):
  ```bash
  pip install webdriver-manager
  ```

---

## Extraction Issues

### CSS Selector Returns `None`

1. Open DevTools in your browser, select the element, and verify the selector.
2. Paste the selector into the browser console: `document.querySelectorAll('your.selector')`.
3. The page may be JavaScript-rendered – switch to `method: selenium`.
4. Content may be inside an `<iframe>` – not accessible with CSS selectors directly.

### Price Extraction Returns `None`

- Call `extract_price()` with the raw text string.
- Unusual currency formats (e.g. `¥1,000`) may need a custom regex.
- Use `extract_by_regex(r'[\d,\.]+')` as a fallback.

---

## Database Issues

### `OperationalError: no such table: products`

Call `db.create_tables()` before inserting data:

```python
db = DatabaseManager()
db.create_tables()   # ← required on first use
```

### Data Not Persisted After Script Finishes

Ensure you are not using `:memory:` as the database path for production workloads; use a file path instead.

---

## Scheduler Issues

### Jobs Not Running

- Ensure `scheduler.start()` was called.
- Check that the scheduler thread is alive (`scheduler.get_jobs()`).
- The main thread must remain running (use a `while True: time.sleep(60)` loop or similar).

### `RuntimeError: Scheduler is already running`

Guard your `start()` call:

```python
if not scheduler._scheduler.running:
    scheduler.start()
```

---

## Performance Optimization

| Tip | Impact |
|---|---|
| Use `insert_products_batch()` instead of looping `insert_product()` | High |
| Reuse a single `WebScraper` instance across pages | Medium |
| Set `delay` to the minimum the target site tolerates | Medium |
| Use SQLite WAL mode for concurrent writes: `PRAGMA journal_mode=WAL;` | Medium |
| Profile with `python -m cProfile your_script.py` | – |

---

## FAQ

**Q: Can I scrape sites that require login?**  
A: Yes – pass session cookies via the `cookies` config key or manipulate `scraper._session.cookies` directly.

**Q: How do I handle CAPTCHAs?**  
A: The scraper does not solve CAPTCHAs automatically. Use a third-party CAPTCHA-solving service or manually obtain a session cookie.

**Q: Is this scraper legal to use?**  
A: Always check a site's `robots.txt` and Terms of Service before scraping. The tool itself is neutral; responsibility lies with the operator.

**Q: Can I run multiple scrapers in parallel?**  
A: Create separate `WebScraper` and `DatabaseManager` instances per thread/process. SQLite supports concurrent reads but only one writer; use PostgreSQL for high-concurrency workloads.

---

## Known Limitations

- Scrapy integration runs via subprocess and does not share the session or cookies with the `requests` backend.
- Selenium support requires a manually installed Chrome + ChromeDriver; headless Firefox is not currently supported out of the box.
- The scheduler uses APScheduler's `BackgroundScheduler` which runs in a daemon thread and will not prevent the process from exiting if the main thread ends.
