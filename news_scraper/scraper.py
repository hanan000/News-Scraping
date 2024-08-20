"""Article scraping for the supported news sources."""

from __future__ import annotations

import json
import logging
import re
from typing import Dict, Iterable, List, Mapping, Optional

import requests
from bs4 import BeautifulSoup

from .base import DEFAULT_TIMEOUT, BaseScraper
from .config import load_config

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)

WEBRAZZI = "WEBRAZZI"
DONANIMHABER = "DONANIMHABER"
WIRED = "WIRED"
THE_VERGE = "THE_VERGE"

# Default HTML selectors per source. Each can be overridden with an
# environment variable of the same name (see .env.example).
DEFAULT_SELECTORS: Dict[str, str] = {
    WEBRAZZI: "single-post-content",
    DONANIMHABER: '["paragraph", "imgparagraph"]',
    WIRED: "body__inner-container",
    THE_VERGE: "duet--article--article-body-component-container",
}
SUPPORTED_SOURCES = tuple(DEFAULT_SELECTORS)

# DonanimHaber paragraphs shorter than this are usually captions or ads.
MIN_PARAGRAPH_LENGTH = 50

_DONANIMHABER_ID = re.compile(r"--(\d+)/?(?:[?#].*)?$")


def normalize_source(name: str) -> str:
    """Map a human-friendly source name to its canonical key.

    ``"The Verge"``, ``"the-verge"`` and ``"THE_VERGE"`` all become ``"THE_VERGE"``.

    Raises:
        ValueError: If the source is not supported.
    """
    key = re.sub(r"[\s\-]+", "_", name.strip()).upper()
    if key not in SUPPORTED_SOURCES:
        supported = ", ".join(SUPPORTED_SOURCES)
        raise ValueError(f"Unsupported news source {name!r}. Supported: {supported}")
    return key


def extract_article_id(url: str) -> Optional[str]:
    """Return the numeric article id at the end of a DonanimHaber URL, if any."""
    match = _DONANIMHABER_ID.search(url)
    return match.group(1) if match else None


class NewsScraper(BaseScraper):
    """Scrapes article text from the supported news sources."""

    def __init__(
        self,
        config: Optional[Mapping[str, str]] = None,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        config = load_config() if config is None else config
        super().__init__(
            user_agent=config.get("SEARCH_USER_AGENT", DEFAULT_USER_AGENT),
            timeout=timeout,
            session=session,
        )
        self.selectors = {
            source: config.get(source, default) for source, default in DEFAULT_SELECTORS.items()
        }

    def parse_article(self, soup: BeautifulSoup, source: str, url: str = "") -> str:
        """Extract the article body from a parsed page as a single string."""
        source = normalize_source(source)
        if source == DONANIMHABER:
            paragraphs = self._donanimhaber_paragraphs(soup, url)
        else:
            paragraphs = [
                p.get_text(strip=True)
                for p in self.find_paragraphs(soup, class_name=self.selectors[source])
            ]
        return " ".join(text for text in paragraphs if text)

    def _donanimhaber_paragraphs(self, soup: BeautifulSoup, url: str) -> List[str]:
        """DonanimHaber marks paragraphs with ids like ``<article id>-paragraph-<n>``."""
        article_id = extract_article_id(url)
        if article_id is None:
            logger.warning("Could not find a DonanimHaber article id in %s", url)
            return []

        prefixes = json.loads(self.selectors[DONANIMHABER])
        id_pattern = re.compile(
            rf"^{article_id}-(?:{'|'.join(map(re.escape, prefixes))})-\d+$"
        )
        # find_all keeps document order, so text and image paragraphs stay interleaved.
        texts = (element.get_text(strip=True) for element in soup.find_all(id=id_pattern))
        return [text for text in texts if len(text) > MIN_PARAGRAPH_LENGTH]

    def scrape(self, urls: Iterable[str], source: str) -> Dict[str, str]:
        """Fetch and parse every URL, returning ``{url: article_text}``.

        URLs that fail to download or yield no text are omitted.
        """
        source = normalize_source(source)
        articles: Dict[str, str] = {}
        for url in urls:
            soup = self.fetch_page(url)
            if soup is None:
                continue
            article = self.parse_article(soup, source, url)
            if article:
                articles[url] = article
            else:
                logger.info("No article content found at %s", url)
        return articles


def scrape_articles(
    urls: Iterable[str], source_name: str, config: Optional[Mapping[str, str]] = None
) -> Dict[str, str]:
    """Scrape articles from one news source.

    Args:
        urls: Article URLs, all from the same source.
        source_name: One of ``Webrazzi``, ``DonanimHaber``, ``Wired`` or
            ``The Verge`` (case, spaces and dashes are ignored).
        config: Optional settings; loaded from ``.env``/the environment if omitted.

    Returns:
        A dictionary mapping each successfully scraped URL to its article text.
    """
    return NewsScraper(config=config).scrape(urls, source_name)
