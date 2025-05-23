import pandas as pd

from algo_royale.backtester.pipeline.data_manage.pipeline_stage import PipelineStage


class DataPreparer:
    def __init__(self, logger):
        self.logger = logger

    def normalize_dataframe(
        self, df: pd.DataFrame, stage: PipelineStage, symbol: str
    ) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Expected DataFrame for {symbol}, got {type(df)}")
        if df.empty:
            self.logger.debug(f"Empty dataframe for {symbol}")
            return df
        df = df.rename(columns=stage.rename_map)
        required = stage.required_columns
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in {symbol} data: {missing}")
        return df

    def prepare_all(self, raw_data, stage: PipelineStage):
        prepared = {}
        for symbol, df in raw_data.items():
            try:
                prepared[symbol] = self.normalize_dataframe(df, stage, symbol)
            except Exception as e:
                self.logger.error(f"Failed to prepare {symbol}: {e}")
        return prepared
