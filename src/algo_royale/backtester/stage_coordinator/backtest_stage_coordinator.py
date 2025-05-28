from logging import Logger
from typing import AsyncIterator, Callable, Dict

import pandas as pd

from algo_royale.backtester.backtest.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.backtester.strategy.strategy_factory import StrategyFactory
from algo_royale.config.config import Config


class BacktestStageCoordinator(StageCoordinator):
    def __init__(
        self,
        config: Config,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        strategy_factory: StrategyFactory,
    ):
        super().__init__(
            stage=BacktestStage.BACKTEST,
            config=config,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.strategy_factory = strategy_factory
        self.executor = StrategyBacktestExecutor(stage_data_manager, logger)

    async def process(
        self, prepared_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """
        Run the backtest and return a dict mapping symbol to a factory that yields result DataFrames.
        """
        # Derive the list of symbols from the prepared_data keys
        ##TODO: get json_path from config
        json_path = self.config.get
        # Use the factory to create strategies for these symbols
        strategies_per_symbol = self.strategy_factory.create_strategies(
            json_path=self.config["strategies_json_path"],
        )
        # Flatten all strategies into a single list for the executor (if needed)
        all_strategies = [
            s for strategies in strategies_per_symbol.values() for s in strategies
        ]

        results: Dict[str, list[pd.DataFrame]] = await self.executor.run_backtest(
            all_strategies, prepared_data
        )

        def make_factory(dfs):
            async def gen():
                for df in dfs:
                    yield df

            return gen

        return {symbol: make_factory(dfs) for symbol, dfs in results.items()}
