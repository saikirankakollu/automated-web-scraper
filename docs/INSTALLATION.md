# Installation Guide

## Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.8 |
| pip | ≥ 21.0 |

---

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/automated-web-scraper.git
cd automated-web-scraper
```

---

## 2. Create and Activate a Virtual Environment

### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows (Command Prompt)
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

---

## 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Optional: Install in Development Mode

```bash
pip install -e .
```

This makes the `webscraper` CLI command available globally within the virtual environment.

---

## 4. Install WebDriver (Selenium Only)

If you plan to use the Selenium backend you need Google Chrome and a matching ChromeDriver.

### Automatic (recommended)

```bash
pip install webdriver-manager
```

Update `src/scraper.py` `scrape_with_selenium` to use `webdriver-manager`:

```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
```

### Manual

1. Download ChromeDriver from <https://chromedriver.chromium.org/downloads> matching your Chrome version.
2. Place the `chromedriver` binary on your `PATH`.

---

## 5. Database Initialisation

The scraper auto-creates the SQLite database and tables on first use.  For
**PostgreSQL**, set the `connection_string` in your config or as an
environment variable:

```bash
export DB_CONNECTION_STRING="postgresql+psycopg2://user:pass@localhost/scraper"
```

---

## 6. Verify Installation

```bash
python -c "from src import WebScraper, DataExtractor; print('OK')"
```

Or run the test suite:

```bash
python -m pytest tests/ -v
```

---

## Platform-Specific Notes

### macOS (Apple Silicon)

`psycopg2-binary` may need to be compiled from source on M1/M2 machines:

```bash
pip install psycopg2 --no-binary psycopg2
```

### Windows

- Ensure `python` and `pip` are on `PATH` (tick the checkbox in the Python installer).
- Use PowerShell or Git Bash for best compatibility.
- `lxml` may require the Visual C++ Build Tools.  Download from
  <https://visualstudio.microsoft.com/visual-cpp-build-tools/>.

### Linux

Install system libraries required by `lxml` and `psycopg2`:

```bash
# Debian / Ubuntu
sudo apt-get install libxml2-dev libxslt1-dev libpq-dev python3-dev

# Fedora / RHEL
sudo dnf install libxml2-devel libxslt-devel postgresql-devel python3-devel
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'lxml'` | Run `pip install lxml` |
| `selenium.common.exceptions.WebDriverException` | Ensure ChromeDriver is on PATH and matches Chrome version |
| `psycopg2.OperationalError: could not connect` | Check PostgreSQL server is running and credentials are correct |
| `scrapy: command not found` | Run `pip install scrapy` or activate your virtual environment |
| Import errors after `pip install -e .` | Re-activate the virtual environment |
