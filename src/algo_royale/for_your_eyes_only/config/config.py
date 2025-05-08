import configparser
import os
from pathlib import Path

# Path to the config.ini file inside the config folder (relative to this file)
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config', 'config.ini')
def _load_ini(section, filename):
    config = configparser.ConfigParser()
    path = Path(__file__).parent / filename
    config.read(path)
    if section in config:
        return config[section]
    else:
        raise Exception(f"Section '{section}' not found in {filename}")
    
# Usage helpers
def _get_config(section):
    return _load_ini(section, "config.ini")

def load_config():
    """
    Loads the configuration from the config.ini file and converts relative paths to absolute paths.
    """
    PATHS = _get_config("paths")

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    # Get the absolute paths based on the location of this script (backtesting folder)
    base_path = os.path.dirname(CONFIG_FILE_PATH)

    return {
        'results_dir': PATHS["results_dir"]
    }