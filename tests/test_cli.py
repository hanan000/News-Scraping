import json

import pytest

from news_scraper import __main__ as cli


def test_cli_prints_articles_as_json(monkeypatch, capsys):
    monkeypatch.setattr(
        cli, "scrape_articles", lambda urls, source: {urls[0]: f"text from {source}"}
    )

    exit_code = cli.main(["wired", "https://www.wired.com/story/x"])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {
        "https://www.wired.com/story/x": "text from wired"
    }


def test_cli_exit_code_when_nothing_scraped(monkeypatch, capsys):
    monkeypatch.setattr(cli, "scrape_articles", lambda urls, source: {})

    assert cli.main(["wired", "https://www.wired.com/story/x"]) == 1
    assert json.loads(capsys.readouterr().out) == {}


def test_cli_rejects_unknown_source(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["bbc", "https://www.bbc.co.uk/news"])

    assert excinfo.value.code == 2
    assert "Unsupported news source" in capsys.readouterr().err
