"""Generic page-fetching helpers shared by all scrapers."""

from __future__ import annotations

import logging
from typing import List, Optional

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # seconds


class BaseScraper:
    """Fetches web pages and provides common HTML extraction helpers."""

    def __init__(
        self,
        user_agent: str,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Download ``url`` and return the parsed HTML, or ``None`` on failure."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Failed to retrieve content from %s: %s", url, exc)
            return None
        return BeautifulSoup(response.text, "html.parser")

    @staticmethod
    def find_paragraphs(soup: BeautifulSoup, class_name: str, tag: str = "div") -> List[Tag]:
        """Return the ``<p>`` elements inside the first ``tag`` with ``class_name``."""
        container = soup.find(tag, class_=class_name)
        if container is None:
            return []
        return container.find_all("p")
