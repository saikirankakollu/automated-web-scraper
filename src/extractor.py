"""HTML data extraction helpers using CSS selectors, tags, and regex."""

import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from src.logger import setup_logger
from src.utils import clean_text, convert_price

logger = setup_logger(__name__)


class DataExtractor:
    """Extract structured data from an HTML document.

    Accepts either a raw HTML string or an existing
    :class:`~bs4.BeautifulSoup` object so callers can reuse a parsed tree.

    Args:
        html_content: Raw HTML string **or** a pre-parsed
            :class:`~bs4.BeautifulSoup` instance.

    Example::

        extractor = DataExtractor("<h1 class='title'>Hello</h1>")
        title = extractor.extract_by_css("h1.title")
        # → "Hello"
    """

    def __init__(self, html_content: Union[str, BeautifulSoup]) -> None:
        if isinstance(html_content, BeautifulSoup):
            self._soup = html_content
        else:
            self._soup = BeautifulSoup(html_content, "lxml")

    # ------------------------------------------------------------------
    # Core extraction primitives
    # ------------------------------------------------------------------

    def extract_by_css(
        self,
        selector: str,
        attribute: Optional[str] = None,
        multiple: bool = False,
    ) -> Union[Optional[str], List[str]]:
        """Extract content using a CSS selector.

        Args:
            selector: CSS selector string (e.g. ``"h1.product-title"``).
            attribute: HTML attribute to read (e.g. ``"href"``).  When
                ``None`` or ``"text"`` the visible text is returned.
            multiple: Return all matches as a list when ``True``.

        Returns:
            A single string (or ``None``) when *multiple* is ``False``,
            or a list of strings when *multiple* is ``True``.
        """
        try:
            elements = self._soup.select(selector)
            if not elements:
                return [] if multiple else None

            def _value(el: Tag) -> str:
                if attribute and attribute != "text":
                    return clean_text(el.get(attribute, "") or "")
                return clean_text(el.get_text())

            if multiple:
                return [_value(el) for el in elements]
            return _value(elements[0]) or None
        except Exception as exc:
            logger.warning("extract_by_css failed for '%s': %s", selector, exc)
            return [] if multiple else None

    def extract_by_tag(
        self,
        tag: str,
        attribute: Optional[str] = None,
        multiple: bool = False,
    ) -> Union[Optional[str], List[str]]:
        """Extract content by HTML tag name.

        Args:
            tag: Tag name (e.g. ``"h1"``, ``"p"``).
            attribute: HTML attribute to read.  ``None`` / ``"text"`` returns
                the text content.
            multiple: Return all matching tags as a list.

        Returns:
            Extracted value(s).
        """
        try:
            elements = self._soup.find_all(tag)
            if not elements:
                return [] if multiple else None

            def _value(el: Tag) -> str:
                if attribute and attribute != "text":
                    return clean_text(el.get(attribute, "") or "")
                return clean_text(el.get_text())

            if multiple:
                return [_value(el) for el in elements]
            return _value(elements[0]) or None
        except Exception as exc:
            logger.warning("extract_by_tag failed for tag '%s': %s", tag, exc)
            return [] if multiple else None

    # ------------------------------------------------------------------
    # Convenience extractors
    # ------------------------------------------------------------------

    def extract_links(self, base_url: Optional[str] = None) -> List[str]:
        """Extract all hyperlink URLs from the document.

        Args:
            base_url: When supplied, relative URLs are resolved against this
                base (e.g. ``"https://example.com"``).

        Returns:
            Deduplicated list of absolute URL strings.
        """
        links: List[str] = []
        for anchor in self._soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if base_url:
                href = urljoin(base_url, href)
            if href and href not in links:
                links.append(href)
        return links

    def extract_images(self, base_url: Optional[str] = None) -> List[str]:
        """Extract all image source URLs from the document.

        Args:
            base_url: When supplied, relative URLs are resolved against this
                base.

        Returns:
            Deduplicated list of image URL strings.
        """
        images: List[str] = []
        for img in self._soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or ""
            src = src.strip()
            if src:
                if base_url:
                    src = urljoin(base_url, src)
                if src not in images:
                    images.append(src)
        return images

    def extract_by_regex(self, pattern: str, group: int = 0) -> Optional[str]:
        """Search the raw HTML for *pattern* and return the first match.

        Args:
            pattern: Regular expression pattern string.
            group: Capture group index to return (0 = entire match).

        Returns:
            Matched string, or ``None`` when the pattern does not match.
        """
        try:
            match = re.search(pattern, str(self._soup))
            if match:
                return match.group(group)
            return None
        except Exception as exc:
            logger.warning("extract_by_regex failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Batch extraction
    # ------------------------------------------------------------------

    def extract_multiple(
        self, selectors_dict: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract multiple named fields in a single call.

        Each entry in *selectors_dict* maps a field name to a spec dict:

        .. code-block:: python

            {
                "name":  {"selector": "h1.title",   "type": "css",  "attribute": "text"},
                "price": {"selector": ".price",      "type": "css",  "attribute": "text"},
                "link":  {"selector": "a.product",   "type": "css",  "attribute": "href"},
            }

        Supported ``"type"`` values: ``"css"`` (default), ``"tag"``,
        ``"regex"``.

        Args:
            selectors_dict: Field-spec mapping as described above.

        Returns:
            Dict mapping field names to their extracted values.
        """
        results: Dict[str, Any] = {}
        for field, spec in selectors_dict.items():
            selector = spec.get("selector", "")
            attr = spec.get("attribute")
            multiple = spec.get("multiple", False)
            field_type = spec.get("type", "css")

            try:
                if field_type == "css":
                    results[field] = self.extract_by_css(selector, attr, multiple)
                elif field_type == "tag":
                    results[field] = self.extract_by_tag(selector, attr, multiple)
                elif field_type == "regex":
                    results[field] = self.extract_by_regex(selector)
                else:
                    logger.warning("Unknown extraction type '%s' for field '%s'.", field_type, field)
                    results[field] = None
            except Exception as exc:
                logger.warning("Failed to extract field '%s': %s", field, exc)
                results[field] = None
        return results

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

    def clean_text(self, text: str) -> str:
        """Strip and normalise whitespace in *text*.

        Args:
            text: Raw text to clean.

        Returns:
            Cleaned string.
        """
        return clean_text(text)

    def extract_price(self, text: str) -> Optional[float]:
        """Parse a price string and return it as a float.

        Handles common currency symbols, thousands separators, and
        European decimal comma notation.

        Args:
            text: Raw price string (e.g. ``"$1,299.99"`` or ``"€49,50"``).

        Returns:
            Price as float, or ``None`` if parsing fails.
        """
        return convert_price(text)
