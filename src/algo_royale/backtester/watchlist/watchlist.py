import os


def load_watchlist(path: str):
    """Load symbols from the watchlist.txt file in the config folder."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Watchlist file not found at: {path}")

    with open(path, "r") as f:
        watchlist = [
            line.strip() for line in f if line.strip()
        ]  # Read each line as a separate symbol

    return watchlist


def save_watchlist(path: str, symbols: list[str]):
    """Save the current list of symbols to the watchlist.txt file."""
    with open(path, "w") as file:
        file.write("\n".join(symbols))  # Save each symbol on a new line
