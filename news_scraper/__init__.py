"""Scrape article text from Webrazzi, DonanimHaber, Wired and The Verge."""

from .scraper import SUPPORTED_SOURCES, NewsScraper, scrape_articles

__all__ = ["NewsScraper", "SUPPORTED_SOURCES", "scrape_articles"]
