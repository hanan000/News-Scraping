from unittest.mock import MagicMock

import pytest
import requests
from bs4 import BeautifulSoup

from news_scraper import scraper as scraper_module
from news_scraper.scraper import (
    DEFAULT_USER_AGENT,
    NewsScraper,
    extract_article_id,
    normalize_source,
    scrape_articles,
)

LONG_1 = "This is the first paragraph and it is comfortably longer than fifty chars."
LONG_2 = "An image paragraph caption that is also long enough to pass the length filter."
LONG_3 = "The closing paragraph of the article, again well over the fifty char minimum."

DONANIMHABER_HTML = f"""
<html><body>
  <p id="180758-paragraph-0">{LONG_1}</p>
  <p id="180758-imgparagraph-0">{LONG_2}</p>
  <p id="180758-paragraph-1">Too short.</p>
  <p id="180758-paragraph-2">{LONG_3}</p>
  <p id="999999-paragraph-0">A paragraph that belongs to a different, related article entirely.</p>
  <p id="180758-sidebar-0">Sidebar content that should be ignored even though it is long.</p>
</body></html>
"""

VERGE_HTML = """
<html><body>
  <div class="duet--article--article-body-component-container">
    <p>First paragraph.</p>
    <p>   </p>
    <p>Second <a href="#">paragraph</a>.</p>
  </div>
  <div class="footer"><p>Not part of the article.</p></div>
</body></html>
"""

DH_URL = "https://www.donanimhaber.com/xiaomi-smart-door-lock-2-pro-tanitildi-iste-fiyati--180758"
VERGE_URL = "https://www.theverge.com/2024/8/20/24224277/example"


def make_response(text="", status=200):
    response = requests.Response()
    response.status_code = status
    response._content = text.encode("utf-8")
    response.encoding = "utf-8"
    return response


def make_scraper(pages, config=None):
    """Build a NewsScraper whose session returns canned responses per URL."""
    session = requests.Session()
    session.get = MagicMock(side_effect=lambda url, **kwargs: pages[url])
    return NewsScraper(config=config or {}, session=session)


@pytest.mark.parametrize(
    "name, expected",
    [
        ("The Verge", "THE_VERGE"),
        ("the-verge", "THE_VERGE"),
        ("THE_VERGE", "THE_VERGE"),
        ("DonanimHaber", "DONANIMHABER"),
        (" wired ", "WIRED"),
        ("Webrazzi", "WEBRAZZI"),
    ],
)
def test_normalize_source(name, expected):
    assert normalize_source(name) == expected


def test_normalize_source_rejects_unknown():
    with pytest.raises(ValueError, match="Unsupported news source"):
        normalize_source("BBC")


@pytest.mark.parametrize(
    "url, expected",
    [
        (DH_URL, "180758"),
        (DH_URL + "/", "180758"),
        (DH_URL + "?utm_source=x", "180758"),
        ("https://www.donanimhaber.com/some-article", None),
    ],
)
def test_extract_article_id(url, expected):
    assert extract_article_id(url) == expected


def test_donanimhaber_keeps_order_and_filters_short_and_foreign_paragraphs():
    soup = BeautifulSoup(DONANIMHABER_HTML, "html.parser")

    text = make_scraper({}).parse_article(soup, "DonanimHaber", DH_URL)

    assert text == f"{LONG_1} {LONG_2} {LONG_3}"


def test_donanimhaber_without_article_id_returns_empty():
    soup = BeautifulSoup(DONANIMHABER_HTML, "html.parser")

    assert make_scraper({}).parse_article(soup, "DonanimHaber", "https://x/no-id") == ""


def test_donanimhaber_prefixes_come_from_config():
    soup = BeautifulSoup(DONANIMHABER_HTML, "html.parser")
    scraper = make_scraper({}, config={"DONANIMHABER": '["imgparagraph"]'})

    assert scraper.parse_article(soup, "DONANIMHABER", DH_URL) == LONG_2


def test_class_based_source_joins_paragraphs():
    soup = BeautifulSoup(VERGE_HTML, "html.parser")

    text = make_scraper({}).parse_article(soup, "The Verge", VERGE_URL)

    assert text == "First paragraph. Second paragraph."


def test_class_based_source_with_missing_container_returns_empty():
    soup = BeautifulSoup("<html><body><p>Nothing here</p></body></html>", "html.parser")

    assert make_scraper({}).parse_article(soup, "Wired", "https://wired.com/x") == ""


def test_selector_override_from_config():
    html = '<div class="custom"><p>Custom body.</p></div>'
    soup = BeautifulSoup(html, "html.parser")
    scraper = make_scraper({}, config={"WEBRAZZI": "custom"})

    assert scraper.parse_article(soup, "Webrazzi", "https://webrazzi.com/x") == "Custom body."


def test_scrape_returns_only_successful_articles():
    pages = {
        VERGE_URL: make_response(VERGE_HTML),
        "https://www.theverge.com/empty": make_response("<html></html>"),
        "https://www.theverge.com/missing": make_response("not found", status=404),
    }
    scraper = make_scraper(pages)

    result = scraper.scrape(list(pages), "The Verge")

    assert result == {VERGE_URL: "First paragraph. Second paragraph."}


def test_scrape_returns_fresh_results_per_call():
    pages = {VERGE_URL: make_response(VERGE_HTML), "https://www.theverge.com/b": make_response(VERGE_HTML)}
    scraper = make_scraper(pages)

    scraper.scrape([VERGE_URL], "The Verge")
    second = scraper.scrape(["https://www.theverge.com/b"], "The Verge")

    assert list(second) == ["https://www.theverge.com/b"]


def test_scrape_rejects_unknown_source_before_fetching():
    scraper = make_scraper({})

    with pytest.raises(ValueError):
        scraper.scrape([VERGE_URL], "BBC")
    scraper.session.get.assert_not_called()


def test_fetch_page_handles_connection_errors():
    session = requests.Session()
    session.get = MagicMock(side_effect=requests.ConnectionError("boom"))
    scraper = NewsScraper(config={}, session=session)

    assert scraper.fetch_page(VERGE_URL) is None


def test_fetch_page_sends_user_agent_and_timeout():
    session = requests.Session()
    session.get = MagicMock(return_value=make_response("<html></html>"))
    scraper = NewsScraper(config={"SEARCH_USER_AGENT": "test-agent"}, session=session, timeout=3)

    scraper.fetch_page(VERGE_URL)

    assert session.headers["User-Agent"] == "test-agent"
    session.get.assert_called_once_with(VERGE_URL, timeout=3)


def test_default_user_agent_when_not_configured():
    assert make_scraper({}).session.headers["User-Agent"] == DEFAULT_USER_AGENT


def test_scrape_articles_wrapper(monkeypatch):
    def fake_get(self, url, **kwargs):
        return make_response(VERGE_HTML)

    monkeypatch.setattr(requests.Session, "get", fake_get)

    result = scrape_articles([VERGE_URL], "the verge", config={})

    assert result == {VERGE_URL: "First paragraph. Second paragraph."}


def test_scrape_articles_loads_config_when_not_given(monkeypatch):
    monkeypatch.setattr(scraper_module, "load_config", lambda: {"WIRED": "custom"})

    assert NewsScraper().selectors["WIRED"] == "custom"
