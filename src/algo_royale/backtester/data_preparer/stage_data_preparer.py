import logging
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.logging.logger_singleton import mockLogger


class StageDataPreparer:
    """Class to prepare data for a specific stage of the backtest pipeline.
    This class is responsible for normalizing the data streams for a given stage,
    validating the DataFrame columns, and preparing the data for processing.

    Parameters:
        stage_data_manager: StageDataManager instance for managing stage data.
        logger: Logger instance for logging information and errors.
    """

    def __init__(self, stage_data_manager: StageDataManager, logger: logging.Logger):
        """
        Initialize the StageDataPreparer with a logger.
        """
        self.logger: logging.Logger = logger
        self.stage_data_manager: StageDataManager = stage_data_manager

    async def normalize_stream(self, stage, iterator_factory):
        iterator = iterator_factory()
        if not hasattr(iterator, "__aiter__"):
            self.logger.error(f"Expected async iterator, got {type(iterator)}")
            raise TypeError(f"Expected async iterator, got {type(iterator)}")
        try:
            async for df in iterator:
                # Validate DataFrame columns
                missing_columns = [
                    col for col in stage.input_columns if col not in df.columns
                ]
                if missing_columns:
                    self.logger.error(
                        f"Missing required columns: {missing_columns} in DataFrame for stage: {stage}"
                    )
                    continue  # Skip invalid DataFrame
                yield df
        finally:
            if hasattr(iterator, "aclose"):
                await iterator.aclose()

    def normalize_stage_data(
        self,
        stage: BacktestStage,
        data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
        strategy_name: Optional[str] = None,
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Prepare data for processing"""
        self.logger.info(f"Preparing data for stage:{stage} | strategy:{strategy_name}")
        prepared_data = {}
        for symbol, df_iter_factory in data.items():

            def factory(symbol=symbol, df_iter_factory=df_iter_factory):
                try:
                    self.logger.info(
                        f"Calling factory for {symbol}, df_iter_factory={df_iter_factory}"
                    )
                    return self.normalize_stream(
                        stage=stage, iterator_factory=df_iter_factory
                    )
                except Exception as e:
                    self.logger.error(
                        f"stage:{stage} | strategy:{strategy_name} data preparation failed: {e}"
                    )
                    self.stage_data_manager.write_error_file(
                        stage=stage,
                        strategy_name=strategy_name,
                        symbol=symbol,
                        filename="prepare_data",
                        error_message=f"stage:{stage} | strategy:{strategy_name} data preparation failed: {e}",
                    )
                    raise

            prepared_data[symbol] = factory
        self.logger.info(
            f"Data prepared for stage:{stage} | strategy:{strategy_name} with {len(prepared_data)} symbols"
        )
        return prepared_data


def mockStageDataPreparer() -> StageDataPreparer:
    """Creates a mock StageDataPreparer for testing purposes."""

    logger: logging.Logger = mockLogger()
    return StageDataPreparer(logger=logger)
