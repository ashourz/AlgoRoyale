import configparser
import os

# Path to the config.ini file inside the config folder (relative to this file)
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config', 'config.ini')

def load_config():
    """
    Loads the configuration from the config.ini file and converts relative paths to absolute paths.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    # Get the absolute paths based on the location of this script (backtesting folder)
    base_path = os.path.dirname(CONFIG_FILE_PATH)

    # Resolve the relative paths to absolute paths
    watchlist_path = os.path.join(base_path, config.get('paths', 'watchlist_path'))
    data_dir = os.path.join(base_path, config.get('paths', 'data_dir'))
    results_dir = os.path.join(base_path, config.get('paths', 'results_dir'))

    return {
        'watchlist_path': watchlist_path,
        'data_dir': data_dir,
        'results_dir': results_dir,
        'initial_capital': config.getfloat('parameters', 'initial_capital'),
        'short_window': config.getint('parameters', 'short_window'),
        'long_window': config.getint('parameters', 'long_window'),
        'start_date': config.get('backtest', 'start_date'),
        'end_date': config.get('backtest', 'end_date'),
        'interval': config.get('backtest', 'interval')
    }