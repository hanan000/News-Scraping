# NewsScraper

NewsScraper is a Python package for scraping articles from various news sources. This package supports multiple news websites, allowing users to extract and aggregate news content for further analysis or processing.

## Features

- Support for Multiple News Sources: Currently supports Webrazzi, DonanimHaber, Wired, and The Verge.
- Customizable Content Extraction: Adjusts scraping strategies based on different site structures.
- Flexible Parsing: Handles various content structures, including paragraphs and images.

## Installation

Make sure you have the following Python packages installed:
- `beautifulsoup4`
- `requests` (if `requests` is used in `BaseScraper`, otherwise adapt accordingly)

You can install these packages using pipenv:

```bash
pipenv install
```

## Usage

### Scraping Articles from DonanimHaber

To scrape articles from DonanimHaber, use the `scrape_donanimhaber_articles` function:

Example: 
```python 
urls = [
    "https://www.donanimhaber.com/xiaomi-smart-door-lock-2-pro-tanitildi-iste-fiyati--180758"
]
articles = scrape_articles(user_id=1, urls=urls, source_name="DonanimHaber")
print(articles)
```


## Project Structure

- **`base/base.py`**: Contains the `BaseScraper` class, which provides basic scraping functionality.
- **`news_scraper.py`**: Contains the `NewsScraper` class with methods for scraping articles from various sources.
- **`utils/`**: Contains utility functions and helper modules used by the scraper.

[//]: # (  - **`helpers.py`**: Includes various helper functions used across different modules.)

[//]: # (  - **`config.py`**: Contains configuration settings for the scraper.)


## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- BeautifulSoup: For parsing HTML content.
- Requests: For HTTP requests (if used).

