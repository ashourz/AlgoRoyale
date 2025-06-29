import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage


class DataPreparer:
    def __init__(self, logger):
        self.logger = logger

    def validate_dataframe(
        self, df: pd.DataFrame, stage: BacktestStage, symbol: str
    ) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Expected DataFrame for {symbol}, got {type(df)}")
        if df.empty:
            self.logger.debug(f"Empty dataframe for {symbol}")
            return df
        required = stage.required_input_columns
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in {symbol} data: {missing}")
        return df
