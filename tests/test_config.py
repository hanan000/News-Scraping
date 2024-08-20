from news_scraper.config import load_config


def test_reads_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("WIRED=custom-class\n")

    config = load_config(env_file=env_file, environ={})

    assert config["WIRED"] == "custom-class"


def test_environment_overrides_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("WIRED=from-file\n")

    config = load_config(env_file=env_file, environ={"WIRED": "from-env"})

    assert config["WIRED"] == "from-env"


def test_missing_env_file_returns_environment_only(tmp_path):
    config = load_config(env_file=tmp_path / "missing.env", environ={"A": "1"})

    assert config == {"A": "1"}


def test_secret_name_is_used_as_path(tmp_path):
    env_file = tmp_path / "secret.env"
    env_file.write_text("WEBRAZZI=from-secret-file\n")

    config = load_config(environ={"SECRET_NAME": str(env_file)})

    assert config["WEBRAZZI"] == "from-secret-file"


def test_prod_reads_secret_contents():
    environ = {"PROJECT_ENV": "prod", "SECRET_NAME": "THE_VERGE=article-body\nWIRED=body\n"}

    config = load_config(environ=environ)

    assert config["THE_VERGE"] == "article-body"
    assert config["WIRED"] == "body"


def test_does_not_mutate_os_environ(tmp_path, monkeypatch):
    import os

    monkeypatch.delenv("ONLY_IN_FILE", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("ONLY_IN_FILE=1\n")

    load_config(env_file=env_file)

    assert "ONLY_IN_FILE" not in os.environ
