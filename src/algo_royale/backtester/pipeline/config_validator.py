##TODO: might not even need this file
class ConfigValidator:
    def __init__(self):
        """Initialize the ConfigValidator with a default configuration."""
        # Default configuration for data columns
        self.default_config = {
            "data_columns": {
                "open_price": "open",
                "high_price": "high",
                "low_price": "low",
                "close_price": "close",
            }
        }

    def validate(self, config):
        """Validate and normalize the configuration."""
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        cfg = {**self.default_config, **config}
        cfg.setdefault("data_columns", self.default_config["data_columns"])
        return cfg
