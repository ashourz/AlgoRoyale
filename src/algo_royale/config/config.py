import os
import configparser

class Config:
    def __init__(self, config_file="config.ini", environment=None):
        """
        Initialize the configuration loader.

        :param config_file: Path to the config.ini file.
        :param environment: Optional, specify the environment (e.g., "development", "production").
        """
        # Initialize the configuration parser and load the file
        self.parser = self._initialize_parser(config_file)

        # Determine the environment (default to "development")
        self.environment = environment or os.getenv("ENV", "development")

    def _initialize_parser(self, config_file):
        """
        Initialize and load the configuration parser.

        :param config_file: Path to the config.ini file.
        :return: ConfigParser instance with the loaded file.
        """
        parser = configparser.ConfigParser()
        parser.read(config_file)
        return parser

    def get(self, section, key, fallback=None):
        """
        Get a configuration value.

        :param section: The section in the config.ini file.
        :param key: The key within the section.
        :param fallback: Value to return if the key is not found.
        :return: The configuration value.
        """
        # Check for environment-specific override
        env_key = f"{section}.{key}".upper().replace(".", "_")
        if env_key in os.environ:
            return os.environ[env_key]

        # Check in environment-specific section
        if self.environment and self.parser.has_section(self.environment):
            env_section = f"{self.environment}:{section}"
            if self.parser.has_option(env_section, key):
                return self.parser.get(env_section, key)

        # Check in the standard section
        if self.parser.has_option(section, key):
            return self.parser.get(section, key)

        # Fallback value
        return fallback

    def get_int(self, section, key, fallback=None):
        """
        Get a configuration value as an integer.
        """
        value = self.get(section, key, fallback)
        return int(value) if value is not None else fallback

    def get_float(self, section, key, fallback=None):
        """
        Get a configuration value as a float.
        """
        value = self.get(section, key, fallback)
        return float(value) if value is not None else fallback

    def get_bool(self, section, key, fallback=None):
        """
        Get a configuration value as a boolean.
        """
        value = self.get(section, key, fallback)
        if value is None:
            return fallback
        return str(value).lower() in ["true", "1", "yes"]

# Initialize the configuration
config = Config()

# Example Usage
if __name__ == "__main__":
    print("Base Directory:", config.get("global", "base_directory"))
    print("Log Level:", config.get("global", "log_level", fallback="INFO"))
    print("Backtesting Data Source:", config.get("backtesting", "data_source"))
    print("Dashboard Refresh Rate (int):", config.get_int("visualization", "dashboard_refresh_rate"))