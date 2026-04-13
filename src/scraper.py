"""Multi-library web scraper with retry logic, proxy support, and UA rotation."""

import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.logger import setup_logger

logger = setup_logger(__name__)

# Realistic browser user-agents for rotation
_USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
]


class WebScraper:
    """Fetch web pages using requests/BeautifulSoup, Selenium, or Scrapy.

    Configuration can be supplied as a dict at construction time or passed
    per-call via keyword arguments.

    Args:
        config: Optional configuration dict.  Recognised top-level keys:

            - ``delay`` – seconds to sleep between requests (default ``2``).
            - ``retry_count`` – maximum retry attempts (default ``3``).
            - ``timeout`` – HTTP timeout in seconds (default ``30``).
            - ``user_agent_rotation`` – rotate User-Agent header (default
              ``True``).
            - ``proxies`` – list of proxy URL strings.
            - ``cookies`` – dict of cookies to include in every request.
            - ``headers`` – extra HTTP headers.

    Example::

        scraper = WebScraper({"delay": 1, "retry_count": 2})
        soup = scraper.scrape_url("https://example.com")
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        cfg = config or {}
        self._delay: float = float(cfg.get("delay", 2))
        self._retry_count: int = int(cfg.get("retry_count", 3))
        self._timeout: int = int(cfg.get("timeout", 30))
        self._ua_rotation: bool = bool(cfg.get("user_agent_rotation", True))
        self._proxies: List[str] = cfg.get("proxies", [])
        self._cookies: Dict[str, str] = cfg.get("cookies", {})
        self._extra_headers: Dict[str, str] = cfg.get("headers", {})
        self._ua_index: int = 0
        self._session: requests.Session = self._build_session()

    # ------------------------------------------------------------------
    # Session / connection helpers
    # ------------------------------------------------------------------

    def _build_session(self) -> requests.Session:
        """Return a :class:`requests.Session` with retry logic configured."""
        session = requests.Session()
        retry = Retry(
            total=self._retry_count,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        if self._cookies:
            session.cookies.update(self._cookies)
        return session

    def _next_user_agent(self) -> str:
        """Return the next User-Agent from the rotation list."""
        ua = _USER_AGENTS[self._ua_index % len(_USER_AGENTS)]
        self._ua_index += 1
        return ua

    def _build_headers(self) -> Dict[str, str]:
        """Assemble request headers, optionally rotating the User-Agent."""
        headers = {
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        if self._ua_rotation:
            headers["User-Agent"] = self._next_user_agent()
        headers.update(self._extra_headers)
        return headers

    def _proxy_dict(self) -> Optional[Dict[str, str]]:
        """Return the next proxy dict or ``None`` when no proxies configured."""
        if not self._proxies:
            return None
        proxy = self._proxies[self._ua_index % len(self._proxies)]
        return {"http": proxy, "https": proxy}

    # ------------------------------------------------------------------
    # Public scraping interface
    # ------------------------------------------------------------------

    def scrape_url(
        self, url: str, method: str = "requests"
    ) -> Optional[BeautifulSoup]:
        """Fetch *url* and return a parsed BeautifulSoup tree.

        Args:
            url: Target URL to fetch.
            method: Scraping backend – ``"requests"`` (default) or
                ``"selenium"``.

        Returns:
            :class:`~bs4.BeautifulSoup` object, or ``None`` on failure.
        """
        if method == "selenium":
            return self.scrape_with_selenium(url)
        return self._scrape_with_requests(url)

    def _scrape_with_requests(self, url: str) -> Optional[BeautifulSoup]:
        """Internal requests-based page fetch with exponential back-off.

        Args:
            url: Target URL.

        Returns:
            Parsed :class:`~bs4.BeautifulSoup` on success, ``None`` on
            permanent failure.
        """
        headers = self._build_headers()
        proxies = self._proxy_dict()

        for attempt in range(1, self._retry_count + 1):
            try:
                time.sleep(self._delay)
                response = self._session.get(
                    url,
                    headers=headers,
                    proxies=proxies,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                logger.info("Fetched %s (attempt %d) – %d bytes", url, attempt, len(response.content))
                return BeautifulSoup(response.text, "lxml")
            except requests.exceptions.HTTPError as exc:
                logger.warning("HTTP error on attempt %d for %s: %s", attempt, url, exc)
                if exc.response is not None and exc.response.status_code < 500:
                    # Client error – no point retrying
                    break
                time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as exc:
                logger.warning("Request failed on attempt %d for %s: %s", attempt, url, exc)
                time.sleep(2 ** attempt)
        logger.error("All attempts exhausted for %s.", url)
        return None

    def scrape_with_selenium(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch *url* using a headless Selenium Chrome browser.

        Requires ``chromedriver`` to be installed and on ``PATH``.

        Args:
            url: Target URL.

        Returns:
            Parsed :class:`~bs4.BeautifulSoup`, or ``None`` on failure.
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.common.exceptions import WebDriverException

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"--user-agent={self._next_user_agent()}")

            driver = webdriver.Chrome(options=options)
            try:
                driver.get(url)
                time.sleep(self._delay)
                html = driver.page_source
                logger.info("Selenium fetched %s", url)
                return BeautifulSoup(html, "lxml")
            finally:
                driver.quit()
        except Exception as exc:
            logger.error("Selenium scraping failed for %s: %s", url, exc)
            return None

    def scrape_with_scrapy(self, url: str) -> Optional[str]:
        """Run a lightweight Scrapy fetch in a subprocess and return raw HTML.

        This uses ``scrapy fetch`` so the main process is not blocked by
        Scrapy's reactor.

        Args:
            url: Target URL.

        Returns:
            Raw HTML string, or ``None`` on failure.
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "scrapy", "fetch", url],
                capture_output=True,
                text=True,
                timeout=self._timeout + 10,
            )
            if result.returncode == 0:
                logger.info("Scrapy fetched %s", url)
                return result.stdout
            logger.error("Scrapy fetch failed for %s: %s", url, result.stderr)
            return None
        except Exception as exc:
            logger.error("scrape_with_scrapy raised for %s: %s", url, exc)
            return None

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying :class:`requests.Session`."""
        self._session.close()
        logger.info("WebScraper session closed.")


def main() -> None:
    """CLI entry-point: print the title of a URL passed as the first argument."""
    if len(sys.argv) < 2:
        print("Usage: webscraper <url>")
        sys.exit(1)
    scraper = WebScraper()
    soup = scraper.scrape_url(sys.argv[1])
    if soup:
        title = soup.find("title")
        print(f"Title: {title.get_text() if title else '(no title)'}")
    else:
        print("Failed to fetch URL.")
