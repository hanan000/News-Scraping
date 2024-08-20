import io
import os
from os import path
from typing import Any

from dotenv import load_dotenv, dotenv_values
import logging as LOG

PROJECT_DIR = path.dirname(path.abspath(__file__)).replace('/utils', '')


def get_project_dir() -> str:
    """Get project directory for binary file, so it can modify the file from the project directory.
       instead from binary temp directory. Like: logs file, csv file.

    Returns:
        Project Directory by using project environment execution path
    """
    return os.path.dirname(os.path.abspath(__file__)).replace('/utils', '')


def get_app_dir() -> str:
    """Returns project base dir

    Returns:
        Project base dir as string
    """
    return PROJECT_DIR


def load_config() -> dict:
    """Loads the environment variables from the '.env' file.

    Returns:
        A dictionary containing the loaded environment variables.
    """
    # Load environment variables from the .env file
    env_file_path = os.environ.get("SECRET_NAME") or path.join(get_app_dir(), ".env")
    temp_dir = path.join(get_app_dir(), ".env")

    try:
        if os.environ.get("PROJECT_ENV") == "prod":
            with open(temp_dir, 'w') as temp_file:
                temp_file.write(io.StringIO(env_file_path).getvalue())

            env_vars = dotenv_values(dotenv_path=temp_dir)
            for key, value in env_vars.items():
                os.environ[key] = str(value)

            os.remove(temp_dir)
            return dict(os.environ)

        elif path.exists(env_file_path):
            load_dotenv(env_file_path)
        return dict(os.environ)

    except (FileNotFoundError, PermissionError, IsADirectoryError, UnicodeDecodeError) as e:
        LOG.exception(f"Error loading .env file: {e}")
    except Exception as e:
        LOG.exception(f"Unexpected error loading .env file: {e}")

    return {}


def get_conf(key: str, default_value=None) -> Any:
    """Gets the value for a given key in the configuration file."""
    config = load_config()
    try:
        return config[key]
    except KeyError:
        LOG.exception(f"`{key}` env variable not found")
        return default_value