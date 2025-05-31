from logging import Logger
from typing import AsyncGenerator, AsyncIterator, Callable

import pandas as pd


class FeatureEngineer:
    def __init__(
        self,
        feature_engineering_func: Callable[[pd.DataFrame], pd.DataFrame],
        logger: Logger,
    ):
        self.feature_engineering_func = feature_engineering_func
        self.logger = logger

    async def engineer_features(
        self, df_iter: AsyncIterator[pd.DataFrame], symbol: str
    ) -> AsyncGenerator[pd.DataFrame, None]:
        """
        Async generator that takes in an async iterator of DataFrames,
        applies feature engineering, and yields the transformed DataFrames.
        """
        async for df in df_iter:
            try:
                self.logger.info(
                    f"Feature engineering input columns: {df.columns}, shape: {df.shape}"
                )
                engineered_df = self.feature_engineering_func(df)
                self.logger.info(
                    f"Feature engineering output columns: {engineered_df.columns}, shape: {engineered_df.shape}"
                )
                if engineered_df.empty:
                    self.logger.warning(
                        f"Engineered DataFrame for {symbol} is empty after feature engineering."
                    )
                    continue
                yield engineered_df
            except Exception as e:
                print(f"Feature engineering failed for {symbol}: {e}")
