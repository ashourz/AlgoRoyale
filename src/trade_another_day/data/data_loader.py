import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=['Date'], index_col='Date')
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    return df
