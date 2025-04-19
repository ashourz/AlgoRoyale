# config/config.py

from configparser import ConfigParser
from pathlib import Path

def load_ini(section, filename):
    config = ConfigParser()
    path = Path(__file__).parent / filename
    config.read(path)
    if section in config:
        return config[section]
    else:
        raise Exception(f"Section '{section}' not found in {filename}")

# Usage helpers
def get_config(section):
    return load_ini(section, "config.ini")

def get_secrets(section):
    return load_ini(section, "secrets.ini")

# Example: Load relevant configs
SETTINGS = get_config("settings")

DB_PARAMS = get_config("database")
DB_SECRETS = get_secrets("database")

DB_USER_PARAMS = get_config("dbuser")
DB_USER_SECRETS = get_secrets("dbuser")

ALPACA_PARAMS = get_config("alpaca")
ALPACA_SECRETS = get_secrets("alpaca")

def get_base_url(env):
    return {
        "test": ALPACA_PARAMS["base_url_trading_paper"],
        "prod": ALPACA_PARAMS["base_url_trading_live"]
    }.get(env, ALPACA_PARAMS["base_url_trading_paper"])  # default to test

ENVIRONMENT = get_config("settings")["environment"]

ALPACA_TRADING_URL = get_base_url(ENVIRONMENT)

TRAINING_PARAMS = get_config("training")

LOGGING_PARAMS = get_config("logging")
