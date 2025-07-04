from datetime import datetime
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager


class SymbolStrategyDataLoader:
    """
    A class to load symbol strategy data for backtesting.
    """

    def __init__(
        self,
        stage_data_manager: StageDataManager,
        stage_data_loader: StageDataLoader,
        logger: Logger,
    ):
        self.stage_data_loader = stage_data_loader
        self.stage_data_manager = stage_data_manager
        self.logger = logger

    async def load(self, stage: BacktestStage):
        """
        Load symbol strategy data from the specified stage.

        Args:
            stage (BacktestStage): The stage from which to load data.

        Returns:
            AsyncIterator[Dict[str, pd.DataFrame]]: An iterator yielding dataframes for each symbol.
        """
        return await self.stage_data_loader.load(stage)

    async def _load_data(
        self,
        stage: BacktestStage,
        start_date: datetime,
        end_date: datetime,
        symbol: Optional[str] = None,
        strategy_name: Optional[str] = None,
        reverse_pages: bool = False,
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Load data based on the configuration"""
        try:
            self.logger.info(
                f"Loading data for stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date}"
            )
            data = await self.stage_data_loader.load_all_stage_data(
                stage=stage,
                strategy_name=strategy_name,
                start_date=self.start_date,
                end_date=self.end_date,
                reverse_pages=reverse_pages,
            )
            return data
        except Exception as e:
            self.logger.error(
                f"stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date} data loading failed: {e}"
            )
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="load_data",
                error_message=f"stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date} data loading failed: {e}",
                start_date=self.start_date,
                end_date=self.end_date,
            )
            return {}

    def _prepare_data(
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
                    return self.data_preparer.normalize_stream(
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
