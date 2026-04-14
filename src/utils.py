"""Utility functions shared across the automated-web-scraper package."""

import csv
import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse


def validate_url(url: str) -> bool:
    """Return ``True`` when *url* is a syntactically valid HTTP/HTTPS URL.

    Args:
        url: The URL string to validate.

    Returns:
        ``True`` if valid, ``False`` otherwise.
    """
    try:
        result = urlparse(url)
        return result.scheme in {"http", "https"} and bool(result.netloc)
    except Exception:
        return False


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """Return an absolute, normalised URL.

    Relative URLs are resolved against *base_url* when provided.

    Args:
        url: The URL (possibly relative) to normalise.
        base_url: Optional base URL used to resolve relative *url* values.

    Returns:
        Absolute URL string.
    """
    if base_url:
        url = urljoin(base_url, url)
    parsed = urlparse(url)
    # Rebuild without fragment to avoid duplicate pages
    normalised = parsed._replace(fragment="").geturl()
    return normalised


def clean_text(text: str) -> str:
    """Strip and normalise whitespace in *text*.

    Args:
        text: Raw text that may contain leading/trailing whitespace or
            runs of internal whitespace characters.

    Returns:
        Cleaned string with normalised internal whitespace.
    """
    if not text:
        return ""
    return " ".join(text.split())


def extract_domain(url: str) -> str:
    """Extract the host/domain portion from *url*.

    Args:
        url: A fully qualified URL.

    Returns:
        Domain string (e.g. ``"example.com"``), or empty string on failure.
    """
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def export_to_csv(data: List[Dict[str, Any]], filepath: str) -> None:
    """Write *data* to a CSV file at *filepath*.

    The file's parent directory is created if it does not exist.  Column
    order follows the keys of the first record.

    Args:
        data: List of dicts where each dict represents one row.
        filepath: Destination file path (e.g. ``"exports/products.csv"``).

    Raises:
        ValueError: If *data* is empty.
    """
    if not data:
        raise ValueError("No data to export.")
    ensure_directory(os.path.dirname(filepath) if os.path.dirname(filepath) else ".")
    fieldnames = list(data[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def export_to_json(data: List[Dict[str, Any]], filepath: str) -> None:
    """Write *data* to a pretty-printed JSON file at *filepath*.

    Args:
        data: List of dicts to serialise.
        filepath: Destination file path.
    """
    ensure_directory(os.path.dirname(filepath) if os.path.dirname(filepath) else ".")
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False, default=str)


def ensure_directory(path: str) -> None:
    """Create *path* and all intermediate directories if they do not exist.

    Args:
        path: Directory path to create.
    """
    if path:
        os.makedirs(path, exist_ok=True)


def convert_price(price_str: str) -> Optional[float]:
    """Parse a price string and return a :class:`float`.

    Handles common currency symbols, thousands separators, and whitespace.

    Args:
        price_str: Raw price string such as ``"$1,299.99"`` or ``"€ 49.50"``.

    Returns:
        Price as a float, or ``None`` if parsing fails.
    """
    if not price_str:
        return None
    cleaned = re.sub(r"[^\d.,]", "", price_str.strip())
    # European format with dot thousands separator: "1.299,99" → "1299.99"
    if re.search(r"\d{1,3}(\.\d{3})+,\d{1,2}$", cleaned):
        cleaned = cleaned.replace(".", "").replace(",", ".")
    # Simple European decimal comma without thousands sep: "9,99" → "9.99"
    elif re.search(r"^\d+,\d{1,2}$", cleaned):
        cleaned = cleaned.replace(",", ".")
    else:
        cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def slugify(text: str) -> str:
    """Convert *text* to a URL-friendly lowercase slug.

    Unicode characters are normalised to their ASCII equivalents where
    possible, then all non-alphanumeric characters are replaced with hyphens.

    Args:
        text: Arbitrary text to slugify.

    Returns:
        Slug string (e.g. ``"hello-world"``).
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate *text* to *max_length* characters, appending ``"…"`` if needed.

    Args:
        text: Text to truncate.
        max_length: Maximum allowed character count (including the ellipsis).

    Returns:
        Original text if it fits, otherwise a truncated string ending in ``"…"``.
    """
    if not text or len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "…"
