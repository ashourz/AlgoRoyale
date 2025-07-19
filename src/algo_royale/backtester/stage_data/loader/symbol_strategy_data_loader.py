from datetime import datetime
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.logging.loggable import Loggable


class SymbolStrategyDataLoader:
    """
    A class to load symbol strategy data for backtesting.
    This class is responsible for loading data for a specific stage of the backtest pipeline,
    including the start and end dates, and optionally filtering by strategy name.
    Parameters:
        stage_data_manager: StageDataManager instance for managing stage data.
        stage_data_loader: StageDataLoader instance for loading data.
        logger: Loggable instance for logging information and errors.
    """

    def __init__(
        self,
        stage_data_manager: StageDataManager,
        stage_data_loader: StageDataLoader,
        logger: Loggable,
    ):
        self.stage_data_loader = stage_data_loader
        self.stage_data_manager = stage_data_manager
        self.logger = logger

    async def load_data(
        self,
        stage: BacktestStage,
        start_date: datetime,
        end_date: datetime,
        strategy_name: Optional[str] = None,
        reverse_pages: bool = False,
        exclude_done_symbols: bool = False,
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Load data based on the configuration"""
        try:
            self.logger.info(
                f"Loading data for stage:{stage} | strategy:{strategy_name} | start_date:{start_date} | end_date:{end_date}"
            )
            data = await self.stage_data_loader.load_all_stage_data(
                stage=stage,
                strategy_name=strategy_name,
                start_date=start_date,
                end_date=end_date,
                reverse_pages=reverse_pages,
                exclude_done_symbols=exclude_done_symbols,
            )
            return data
        except Exception as e:
            self.logger.error(
                f"stage:{stage} | strategy:{strategy_name} | start_date:{start_date} | end_date:{end_date} data loading failed: {e}"
            )
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                filename="load_data",
                error_message=f"stage:{stage} | strategy:{strategy_name} | start_date:{start_date} | end_date:{end_date} data loading failed: {e}",
                start_date=start_date,
                end_date=end_date,
            )
            return {}
