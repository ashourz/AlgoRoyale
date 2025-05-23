from typing import AsyncGenerator, AsyncIterator

import pandas as pd
from algo_royale.backtester.iii_feature_engineering import feature_engineering


class FeatureEngineer:
    async def engineer_features(
        self, df_iter: AsyncIterator[pd.DataFrame], symbol: str
    ) -> AsyncGenerator[pd.DataFrame, None]:
        """
        Async generator that takes in an async iterator of DataFrames,
        applies feature engineering, and yields the transformed DataFrames.
        """
        async for df in df_iter:
            try:
                engineered_df = feature_engineering(df)
                yield engineered_df
            except Exception as e:
                # Optionally log or handle errors per symbol
                print(f"Feature engineering failed for {symbol}: {e}")
