"""Configuration loading for the news scraper.

Settings are read from a ``.env`` file in the project root (see ``.env.example``)
and can be overridden by real environment variables.

Two special variables control where the settings come from:

* ``SECRET_NAME`` - path to an alternative ``.env`` file.
* ``PROJECT_ENV=prod`` - in production, ``SECRET_NAME`` holds the *contents*
  of the ``.env`` file (for example, injected from a secrets manager) rather
  than a path.
"""

from __future__ import annotations

import io
import logging
import os
from pathlib import Path
from typing import Dict, Mapping, Optional

from dotenv import dotenv_values

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = PROJECT_DIR / ".env"


def _read_dotenv(env: Mapping[str, str], env_file: Optional[Path]) -> Dict[str, str]:
    """Return the key/value pairs defined by the configured dotenv source."""
    secret = env.get("SECRET_NAME")

    if env.get("PROJECT_ENV") == "prod" and secret:
        values = dotenv_values(stream=io.StringIO(secret))
    else:
        path = Path(env_file or secret or DEFAULT_ENV_FILE)
        if not path.is_file():
            logger.debug("No .env file found at %s", path)
            return {}
        values = dotenv_values(path)

    return {key: value for key, value in values.items() if value is not None}


def load_config(
    env_file: Optional[Path] = None, environ: Optional[Mapping[str, str]] = None
) -> Dict[str, str]:
    """Load settings from the dotenv source, overridden by environment variables.

    Args:
        env_file: Explicit path to a ``.env`` file. Defaults to ``SECRET_NAME``
            or ``<project root>/.env``.
        environ: Environment mapping to use instead of ``os.environ``
            (mainly useful for tests).

    Returns:
        A new dictionary of settings. ``os.environ`` is never modified.
    """
    env = os.environ if environ is None else environ
    config = _read_dotenv(env, env_file)
    config.update(env)
    return config
