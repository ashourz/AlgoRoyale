import pandas as pd

class DataPreparer:
    def __init__(self, logger):
        self.logger = logger

    def normalize_dataframe(self, df: pd.DataFrame, config: dict, symbol: str) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Expected DataFrame for {symbol}, got {type(df)}")
        if df.empty:
            self.logger.debug(f"Empty dataframe for {symbol}")
            return df
        df = df.rename(columns=config['data_columns'])
        required = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in {symbol} data: {missing}")
        return df

    def prepare_all(self, raw_data, config):
        prepared = {}
        for symbol, df in raw_data.items():
            try:
                prepared[symbol] = self.normalize_dataframe(df, config, symbol)
            except Exception as e:
                self.logger.error(f"Failed to prepare {symbol}: {e}")
        return prepared