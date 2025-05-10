# config/config.py

from configparser import ConfigParser
import logging
from pathlib import Path

def _load_ini(section, filename):
    config = ConfigParser()
    path = Path(__file__).parent / filename
    config.read(path)
    if section in config:
        return config[section]
    else:
        raise Exception(f"Section '{section}' not found in {filename}")

# Usage helpers
def _get_config(section):
    return _load_ini(section, "config.ini")

def _get_secrets(section):
    return _load_ini(section, "secrets.ini")

# Example: Load relevant configs
SETTINGS = _get_config("settings")

DB_PARAMS = _get_config("database")
DB_SECRETS = _get_secrets("database")

DB_USER_PARAMS = _get_config("dbuser")
DB_USER_SECRETS = _get_secrets("dbuser")

ALPACA_PARAMS = _get_config("alpaca")
ALPACA_SECRETS = _get_secrets("alpaca")

def get_base_url(env):
    return {
        "test": ALPACA_PARAMS["base_url_trading_paper"],
        "prod": ALPACA_PARAMS["base_url_trading_live"]
    }.get(env, ALPACA_PARAMS["base_url_trading_paper"])  # default to test

ENVIRONMENT = _get_config("settings")["environment"]

ALPACA_TRADING_URL = get_base_url(ENVIRONMENT)

TRAINING_PARAMS = _get_config("training")

LOGGING_PARAMS = _get_config("logging")

def get_logging_level() -> int:
    level_str = LOGGING_PARAMS.get("level", "INFO").upper()
    return getattr(logging, level_str, logging.INFO)