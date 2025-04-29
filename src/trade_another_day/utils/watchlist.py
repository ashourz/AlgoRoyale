import os

import os

# Path to the config directory where the watchlist.txt resides
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
WATCHLIST_FILE = os.path.join(CONFIG_DIR, 'watchlist.txt')

def load_watchlist():
    """Load symbols from the watchlist.txt file in the config folder."""
    if not os.path.exists(WATCHLIST_FILE):
        raise FileNotFoundError(f"Watchlist file not found at: {WATCHLIST_FILE}")
    
    with open(WATCHLIST_FILE, 'r') as file:
        watchlist = file.read().splitlines()  # Read each line as a separate symbol
    
    return watchlist

def save_watchlist(symbols):
    """Save the current list of symbols to the watchlist.txt file."""
    with open(WATCHLIST_FILE, 'w') as file:
        file.write("\n".join(symbols))  # Save each symbol on a new line
