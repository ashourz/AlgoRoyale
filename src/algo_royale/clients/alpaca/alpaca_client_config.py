## src/algo_royale/live_trading/config/config.py


from typing import Optional


class TradingConfig:
    """
    Configuration class for Alpaca trading parameters.
    """
    def __init__(self, config, secrets):
        self.environment = config.get("global", "environment")
        self.alpaca_params = config.get_section("alpaca")
        self.alpaca_secrets = secrets.get_section("alpaca")
        self.alpaca_trading_url = self.get_base_url(self.environment)
    
    def get_base_url(self, env: Optional[str] = None) -> str:
        return {
            "test": self.alpaca_params["base_url_trading_paper"],
            "prod": self.alpaca_params["base_url_trading_live"],
        }.get(env or self.environment, self.alpaca_params["base_url_trading_paper"])  # default to test

