import os
import pandas as pd
from trade_another_day.utils.watchlist import load_watchlist

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def _load_data_for_symbol(symbol: str, fetch_if_missing=True) -> pd.DataFrame:
    """
    Load bar data for a given symbol. If data does not exist, optionally fetch it.
    """
    filename = os.path.join(DATA_DIR, f"{symbol}.csv")

    if os.path.exists(filename):
        return pd.read_csv(filename, parse_dates=["datetime"])

    if fetch_if_missing:
        print(f"[INFO] Data for {symbol} not found locally. Attempting to fetch...")
        df = _fetch_data_for_symbol(symbol)
        if df is not None:
            df.to_csv(filename, index=False)
            return df
        else:
            raise ValueError(f"[ERROR] Failed to fetch data for {symbol}")

    raise FileNotFoundError(f"No local data found for {symbol}, and fetching is disabled.")

def _fetch_data_for_symbol(symbol: str) -> pd.DataFrame:
    """
    Placeholder function to fetch data from an external API.
    Replace this with actual API logic.
    """
    # TODO: Implement data fetching logic here.
    raise NotImplementedError("Fetching logic not implemented. Please integrate your data source.")

def load_all_watchlist_data(fetch_if_missing=True) -> dict:
    """
    Loads data for all symbols in the watchlist.
    Returns a dict of {symbol: DataFrame}
    """
    watchlist = load_watchlist()
    data = {}

    for symbol in watchlist:
        try:
            data[symbol] = _load_data_for_symbol(symbol, fetch_if_missing=fetch_if_missing)
        except Exception as e:
            print(f"[WARN] Could not load data for {symbol}: {e}")

    return data
