import requests
from bs4 import BeautifulSoup
from utils import get_conf


class BaseScraper:
    """A parent class with common scraping functionality."""

    def __init__(self, user_id):
        self.headers = {"User-Agent": get_conf("SEARCH_USER_AGENT")}
        self.user_id = user_id

    def fetch_page(self, url: str) -> BeautifulSoup or None:
        """Fetch the content of the page."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Failed to retrieve content from {url}: {e}")
            return None

    @staticmethod
    def get_content(soup: BeautifulSoup, tag: str, class_name: str, scraping_type: str = None):
        """Extract the useful content from the web page."""
        main_content = soup.find(tag, class_=class_name)
        if main_content:
            return main_content.find_all('p') if scraping_type == "News" else main_content
        return []