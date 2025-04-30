import os
import pandas as pd
from trade_another_day.utils.watchlist import load_watchlist

def ensure_dir_exists(path: str):
    os.makedirs(path, exist_ok=True)

def _load_data_for_symbol(symbol: str, data_dir: str, fetch_if_missing=True) -> pd.DataFrame:
    """
    Load bar data for a given symbol. If data does not exist, optionally fetch it.
    """
    ensure_dir_exists(data_dir)
    filepath = os.path.join(data_dir, f"{symbol}.csv")

    if os.path.exists(filepath):
        return pd.read_csv(filepath, parse_dates=["datetime"])

    if fetch_if_missing:
        print(f"[INFO] Data for {symbol} not found locally. Attempting to fetch...")
        df = _fetch_data_for_symbol(symbol)
        if df is not None:
            df.to_csv(filepath, index=False)
            return df
        else:
            raise ValueError(f"[ERROR] Failed to fetch data for {symbol}")

    raise FileNotFoundError(f"No local data found for {symbol}, and fetching is disabled.")

def _fetch_data_for_symbol(symbol: str) -> pd.DataFrame:
    """
    Placeholder function to fetch data from an external API.
    Replace this with actual API logic.
    """
    raise NotImplementedError("Fetching logic not implemented. Please integrate your data source.")

def load_all_symbol_data_from_watchlist(
    watchlist_path: str,
    data_dir: str,
    fetch_if_missing=True
) -> dict[str, pd.DataFrame]:
    """
    Loads data for all symbols in the specified watchlist file.
    
    Args:
        watchlist_path: Full path to the watchlist .txt file
        data_dir: Directory to store and load .csv files
        fetch_if_missing: If True, fetch data when .csv is missing

    Returns:
        Dict of {symbol: pd.DataFrame}
    """
    watchlist = load_watchlist(watchlist_path)
    data = {}

    for symbol in watchlist:
        try:
            data[symbol] = _load_data_for_symbol(symbol, data_dir, fetch_if_missing)
        except Exception as e:
            print(f"[WARN] Could not load data for {symbol}: {e}")

    return data
