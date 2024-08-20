"""Command-line entry point: ``python -m news_scraper SOURCE URL [URL ...]``."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import List, Optional

from .scraper import SUPPORTED_SOURCES, scrape_articles


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="news_scraper",
        description="Scrape article text from supported news sites and print it as JSON.",
    )
    parser.add_argument(
        "source",
        help=f"news source, one of: {', '.join(SUPPORTED_SOURCES)} (case-insensitive)",
    )
    parser.add_argument("urls", nargs="+", metavar="URL", help="article URL(s) to scrape")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    try:
        articles = scrape_articles(args.urls, args.source)
    except ValueError as exc:
        parser.error(str(exc))

    json.dump(articles, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if articles else 1


if __name__ == "__main__":
    sys.exit(main())
