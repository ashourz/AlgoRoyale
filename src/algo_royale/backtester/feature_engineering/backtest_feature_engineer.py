from typing import AsyncGenerator, AsyncIterator, Callable

import pandas as pd

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.logging.loggable import Loggable
from algo_royale.logging.logger_factory import mockLogger


class BacktestFeatureEngineer:
    def __init__(
        self,
        feature_engineering_func: Callable[[pd.DataFrame], pd.DataFrame],
        logger: Loggable,
        max_lookback: int,
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
                self.logger.debug(f"Processing DataFrame for {symbol}: {df.shape}")

                # Validate the input DataFrame
                if not self._validate_input(df):
                    self.logger.error(
                        f"Input DataFrame for {symbol} is invalid. Skipping feature engineering."
                    )
                    continue
                # Prepend buffer if it exists
                if buffer is not None and not buffer.empty:
                    df = pd.concat([buffer, df], ignore_index=True)

                self.logger.info(
                    f"Feature engineering input columns: {df.columns}, shape: {df.shape}"
                )
                engineered_df: pd.DataFrame = self.feature_engineering_func(
                    df=df, logger=self.logger
                )
                # Validate the output DataFrame
                if not self._validate_output(engineered_df):
                    self.logger.error(
                        f"Output DataFrame for {symbol} is invalid after feature engineering."
                    )
                    continue
                # Only yield the rows corresponding to the current page
                # (i.e., drop the buffer rows)
                if buffer is not None and not buffer.empty:
                    output_df = engineered_df.iloc[self.max_lookback :]
                else:
                    output_df = engineered_df

                self.logger.info(
                    f"Feature engineering output columns: {engineered_df.columns}, shape: {engineered_df.shape}"
                )
                self.logger.debug(
                    f"Yielding engineered DataFrame for {symbol} with shape: {output_df.shape}"
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

    def _validate_input(self, df: pd.DataFrame) -> bool:
        """
        Validate the DataFrame to ensure it has the required columns.
        This method can be customized based on the specific requirements of your feature engineering function.
        """
        required_input_columns = BacktestStage.FEATURE_ENGINEERING.input_columns
        self.logger.debug(
            f"Validating input DataFrame columns: {df.columns}, expected: {required_input_columns}"
        )
        if not required_input_columns:
            self.logger.error(
                "No input columns defined for feature engineering. Cannot validate input."
            )
            return False
        missing_columns = [
            col for col in required_input_columns if col not in df.columns
        ]
        if missing_columns:
            self.logger.error(
                f"Missing required columns: {missing_columns} in DataFrame."
            )
            return False
        return True

    def _validate_output(self, df: pd.DataFrame) -> bool:
        """
        Validate the DataFrame to ensure it has the expected output columns.
        This method can be customized based on the specific requirements of your feature engineering function.
        """
        required_output_columns = BacktestStage.FEATURE_ENGINEERING.output_columns
        self.logger.debug(
            f"Validating output DataFrame columns: {df.columns}, expected: {required_output_columns}"
        )
        if not required_output_columns:
            self.logger.error(
                "No output columns defined for feature engineering. Cannot validate output."
            )
            return False
        missing_columns = [
            col for col in required_output_columns if col not in df.columns
        ]
        if missing_columns:
            self.logger.error(
                f"Missing expected output columns: {missing_columns} in DataFrame."
            )
            return False
        return True


def mockFeatureEngineer(
    feature_engineering_func: Callable[[pd.DataFrame], pd.DataFrame],
    max_lookback=200,
) -> BacktestFeatureEngineer:
    """
    Create a mock FeatureEngineer instance for testing purposes.
    """
    return BacktestFeatureEngineer(
        feature_engineering_func=feature_engineering_func,
        logger=mockLogger(),
        max_lookback=max_lookback,
    )
