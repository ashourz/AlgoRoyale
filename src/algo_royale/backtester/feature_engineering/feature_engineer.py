from logging import Logger
from typing import AsyncGenerator, AsyncIterator, Callable

import pandas as pd


class FeatureEngineer:
    def __init__(
        self,
        feature_engineering_func: Callable[[pd.DataFrame], pd.DataFrame],
        logger: Logger,
        max_lookback=200,  # Default to 200, can be adjusted based on your needs
        # This should match the max window/lag you use in your feature engineering function
    ):
        self.feature_engineering_func = feature_engineering_func
        self.logger = logger
        self.max_lookback = max_lookback  # Set this to the max window/lag you use

    async def engineer_features(
        self, df_iter: AsyncIterator[pd.DataFrame], symbol: str
    ) -> AsyncGenerator[pd.DataFrame, None]:
        buffer = None  # Will hold the last N rows from the previous page

        async for df in df_iter:
            try:
                # Prepend buffer if it exists
                if buffer is not None and not buffer.empty:
                    df = pd.concat([buffer, df], ignore_index=True)

                self.logger.info(
                    f"Feature engineering input columns: {df.columns}, shape: {df.shape}"
                )
                engineered_df: pd.DataFrame = self.feature_engineering_func(
                    df=df, logger=self.logger
                )

                # Only yield the rows corresponding to the current page
                # (i.e., drop the buffer rows)
                if buffer is not None and not buffer.empty:
                    output_df = engineered_df.iloc[self.max_lookback :]
                else:
                    output_df = engineered_df

                self.logger.info(
                    f"Feature engineering output columns: {engineered_df.columns}, shape: {engineered_df.shape}"
                )
                if output_df.empty:
                    self.logger.warning(
                        f"Engineered DataFrame for {symbol} is empty after feature engineering."
                    )
                    continue
                yield output_df

                # Update buffer to last N rows of the *input* DataFrame
                buffer = df.iloc[-self.max_lookback :].copy()
            except Exception as e:
                self.logger.error(f"Feature engineering failed for {symbol}: {e}")
