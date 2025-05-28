from typing import AsyncGenerator, AsyncIterator, Callable

import pandas as pd


class FeatureEngineer:
    def __init__(
        self, feature_engineering_func: Callable[[pd.DataFrame], pd.DataFrame]
    ):
        self.feature_engineering_func = feature_engineering_func

    async def engineer_features(
        self, df_iter: AsyncIterator[pd.DataFrame], symbol: str
    ) -> AsyncGenerator[pd.DataFrame, None]:
        """
        Async generator that takes in an async iterator of DataFrames,
        applies feature engineering, and yields the transformed DataFrames.
        """
        async for df in df_iter:
            try:
                engineered_df = self.feature_engineering_func(df)
                yield engineered_df
            except Exception as e:
                # Optionally log or handle errors per symbol
                print(f"Feature engineering failed for {symbol}: {e}")
