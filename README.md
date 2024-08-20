# News Scraping

A small Python library and command-line tool that downloads news articles and
extracts their body text. It supports four sites:

| Source       | Name to pass      | How the article body is found                                   |
|--------------|-------------------|-----------------------------------------------------------------|
| Webrazzi     | `Webrazzi`        | `<p>` tags inside `div.single-post-content`                     |
| DonanimHaber | `DonanimHaber`    | elements with ids `<article id>-paragraph-<n>` / `-imgparagraph-<n>` |
| Wired        | `Wired`           | `<p>` tags inside `div.body__inner-container`                   |
| The Verge    | `The Verge`       | `<p>` tags inside `div.duet--article--article-body-component-container` |

Source names are case-insensitive, and spaces, dashes and underscores are
interchangeable (`the-verge`, `THE_VERGE` and `The Verge` all work).

## Features

- Scrape one or many article URLs from a source in a single call.
- Returns a plain `{url: article_text}` dictionary; pages that fail to download
  or contain no article text are skipped and logged.
- DonanimHaber text and image paragraphs are kept in page order, and short
  fragments (50 characters or fewer, e.g. captions) are dropped.
- Per-site selectors and the User-Agent header can be overridden through a
  `.env` file or environment variables, so a site redesign does not require a
  code change.
- Requests use a timeout and a shared HTTP session.

## Requirements

- Python 3.9+
- `requests`, `beautifulsoup4`, `python-dotenv` (pinned in `Pipfile` and
  `requirements.txt`)

## Setup

With pipenv:

```bash
pipenv install --dev
pipenv shell
```

Or with pip and a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # or requirements.txt for runtime only
```

### Configuration (optional)

The scraper works without any configuration. To change the User-Agent or a
site's selector, copy the example file and edit it:

```bash
cp .env.example .env
```

| Variable            | Purpose                                                        |
|---------------------|----------------------------------------------------------------|
| `SEARCH_USER_AGENT` | `User-Agent` header sent with every request                    |
| `WEBRAZZI`, `WIRED`, `THE_VERGE` | CSS class of the `<div>` that wraps the article body |
| `DONANIMHABER`      | JSON list of paragraph id prefixes, e.g. `["paragraph", "imgparagraph"]` |

Real environment variables take precedence over values in `.env`. You can
point to a different file with `SECRET_NAME=/path/to/file.env`; with
`PROJECT_ENV=prod`, `SECRET_NAME` is instead read as the *contents* of a
`.env` file (useful when it is injected from a secrets manager).

## Usage

### Command line

```bash
python -m news_scraper SOURCE URL [URL ...]
```

```bash
python -m news_scraper DonanimHaber \
  "https://www.donanimhaber.com/xiaomi-smart-door-lock-2-pro-tanitildi-iste-fiyati--180758"
```

The result is printed as JSON. The exit code is `1` if no article could be
scraped and `2` for an unknown source.

### Python

```python
from news_scraper import scrape_articles

articles = scrape_articles(
    urls=["https://www.donanimhaber.com/xiaomi-smart-door-lock-2-pro-tanitildi-iste-fiyati--180758"],
    source_name="DonanimHaber",
)
for url, text in articles.items():
    print(url, text[:200])
```

For several batches, create a `NewsScraper` once and reuse its HTTP session:

```python
from news_scraper import NewsScraper

scraper = NewsScraper(timeout=15)
verge = scraper.scrape(["https://www.theverge.com/..."], "The Verge")
wired = scraper.scrape(["https://www.wired.com/story/..."], "Wired")
```

### Example output

```json
{
  "https://www.donanimhaber.com/xiaomi-smart-door-lock-2-pro-tanitildi-iste-fiyati--180758": "Gelişen teknolojiden kapı kilitleri de nasibini alırken artık önemli bir rekabet yaşanacak duruma geldi. Her yeni piyasaya çıkan model bir öncekinden daha iddialı özelliklerle geliyor. Xiaomi Smart Door Lock 2 Pro kapınıza bir bilgisayar donanımı entegre ediyor. ..."
}
```

> **Note:** scraping depends on each site's HTML. When a site changes its
> markup, the selector for that source stops matching and the URL is skipped;
> update the corresponding variable in `.env` to fix it.

## Project structure

```
.
├── news_scraper/
│   ├── __init__.py     # public API: scrape_articles, NewsScraper, SUPPORTED_SOURCES
│   ├── __main__.py     # command-line interface
│   ├── base.py         # BaseScraper: HTTP fetching and generic HTML helpers
│   ├── config.py       # .env / environment loading
│   └── scraper.py      # NewsScraper and per-source parsing rules
├── tests/              # pytest suite (network calls are mocked)
├── .env.example        # documented configuration template
├── Pipfile / Pipfile.lock
├── requirements.txt / requirements-dev.txt
└── pytest.ini
```

## Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests never touch the network: HTTP responses are mocked and socket
connections are blocked by a fixture in `tests/conftest.py`.

## License

MIT. See [LICENSE.md](LICENSE.md).
