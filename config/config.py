# config/config.py

from configparser import ConfigParser
from pathlib import Path

def get_config(section="postgres"):
    config = ConfigParser()
    path = Path(__file__).parent / "config.ini"
    config.read(path)
    if section in config:
        return config[section]
    else:
        raise Exception(f"Section {section} not found in config.ini")

# Load database parameters
DB_PARAMS = get_config("database")
ALPACA_PARAMS = get_config("alpaca")


# Optionally, you can print out the DB_PARAMS to verify the connection values are correct
# print(DB_PARAMS)