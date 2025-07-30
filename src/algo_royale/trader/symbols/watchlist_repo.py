import os


class WatchlistRepo:
    """Repository for managing the watchlist of symbols.
    This class provides methods to load and save the watchlist from/to a file."""

    def __init__(self, watchlist_path: str):
        self.watchlist_path = watchlist_path
        if not os.path.exists(self.watchlist_path):
            raise FileNotFoundError(
                f"Watchlist file not found at: {self.watchlist_path}"
            )

    def load_watchlist(self):
        """Load symbols from the watchlist.txt file in the config folder."""
        if not os.path.exists(self.watchlist_path):
            raise FileNotFoundError(
                f"Watchlist file not found at: {self.watchlist_path}"
            )

        with open(self.watchlist_path, "r") as f:
            watchlist = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]  # Read each line as a separate symbol

        return watchlist

    def save_watchlist(self, symbols: list[str]):
        """Save the current list of symbols to the watchlist.txt file."""
        if not symbols:
            raise ValueError("Cannot save an empty watchlist.")
        with open(self.watchlist_path, "w") as file:
            file.write("\n".join(symbols))  # Save each symbol on a new line
