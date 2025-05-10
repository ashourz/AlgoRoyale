## src/algo_royale/live_trading/config/config.py

from algo_royale.config.config import config, secrets


DB_PARAMS = config.get_section("database")
DB_SECRETS = secrets.get_section("database")

DB_USER_PARAMS = config.get_section("dbuser")
DB_USER_SECRETS = secrets.get_section("dbuser")

ALPACA_PARAMS = config.get_section("alpaca")
ALPACA_SECRETS = secrets.get_section("alpaca")

def get_base_url(env):
    return {
        "test": config.get("alpaca", "base_url_trading_paper"),
        "prod": config.get("alpaca", "base_url_trading_live"),
    }.get(env, config.get("alpaca", "base_url_trading_paper"))  # default to test

ENVIRONMENT = config.get("global", "environment")

ALPACA_TRADING_URL = get_base_url(ENVIRONMENT)
