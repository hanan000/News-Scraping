import re
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

from base.base import BaseScraper
from utils import get_conf


class NewsScraper(BaseScraper):
    """Scrapes product data from various news sources."""

    def __init__(self, user_id: int):
        super().__init__(user_id=user_id)
        self.articles = {}

    @staticmethod
    def extract_text(element: BeautifulSoup, min_length: int = 50) -> Optional[str]:
        """Extracts and returns text from a BeautifulSoup element if it meets the minimum length."""
        text = element.get_text(strip=True)
        return text if len(text) > min_length else None

    def parse_content(self, soup: BeautifulSoup, base_id: str, source_name: str) -> str:
        """Extracts and concatenates text content from specified elements."""

        if source_name == "DONANIMHABER":
            source_classes = eval(get_conf(source_name, ["", ""]))
            p_id, imp_id = (
                source_classes[0],
                source_classes[1] if len(source_classes) > 1 else "",
            )
            paragraphs = [soup.find(id=f"{base_id}-{p_id}-{i}") for i in range(100)] + [
                soup.find(id=f"{base_id}-{imp_id}-{i}") for i in range(100)
            ]
            content = [self.extract_text(p) for p in paragraphs if p]
        else:
            content_div = self.get_content(
                soup,
                tag="div",
                class_name=get_conf(source_name, ""),
                scraping_type="News",
            )
            content = [p.get_text(strip=True) for p in content_div] or []

        return " ".join(filter(None, content))

    def get_articles(
        self, urls: List, base_ids: Optional[List], source_name: str = None
    ) -> List:
        """Fetches and parses articles from the provided URLs."""
        for url, base_id in zip(urls, base_ids or [""] * len(urls)):
            soup = self.fetch_page(url)
            if not soup:
                continue

            article = self.parse_content(soup, base_id, source_name)
            if article:
                self.articles[url] = article

        return self.articles


def scrape_articles(user_id: int, urls: List[str], source_name: str) -> Dict[str, str]:
    """Scrapes articles from a given news source based on provided URLs.

    If the source is 'DonanimHaber', it extracts the article ID from the URLs.
    For other sources, it directly uses the URLs.

    Args:
        user_id (int): The user ID for the scraper.
        urls (List[str]): List of URLs to scrape.
        source_name (str): The name of the news source.

    Returns:
        A dictionary where keys are URLs and values are the scraped article content.
    """

    def extract_id_from_url(url: str) -> Optional[str]:
        """Extracts the article ID from the URL."""
        match = re.search(r"--(\d+)$", url)
        return match.group(1) if match else None

    scraper = NewsScraper(user_id=user_id)

    base_ids = (
        [extract_id_from_url(url) for url in urls] if source_name == "DONANIMHABER" else None
    )
    return scraper.get_articles(urls, base_ids, source_name)


if __name__ == "__main__":
    urls = [
        "https://www.donanimhaber.com/xiaomi-smart-door-lock-2-pro-tanitildi-iste-fiyati--180758",
        # "https://www.theverge.com/2024/8/20/24224277/disney-wrongful-death-lawsuit-waiving-arbitration",
        # "https://webrazzi.com/2024/08/20/apple-podcastsin-web-uygulamasi-yayina-alindi"
        # 'https://www.wired.com/sponsored/story/bespoke-sound-montblanc-wireless-earphones-mtb03/'


    ]
    # source_names
    # THE_VERGE
    # DONANIMHABER
    # WIRED
    # WEBRAZZI

    articles = scrape_articles(user_id=1, urls=urls, source_name="DONANIMHABER")
    print(articles)
