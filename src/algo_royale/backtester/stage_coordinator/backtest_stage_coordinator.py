from typing import AsyncIterator, Callable, Dict

import pandas as pd

from algo_royale.backtester.backtest.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator


class BacktestStageCoordinator(StageCoordinator):
    def __init__(
        self,
        config,
        data_loader,
        data_preparer,
        data_writer,
        stage_data_manager,
        logger,
        strategies,
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
        self.strategies = strategies
        self.executor = StrategyBacktestExecutor(stage_data_manager, logger)

    async def process(
        self, prepared_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """
        Run the backtest and return a dict mapping symbol to a factory that yields result DataFrames.
        """
        results: Dict[str, list[pd.DataFrame]] = await self.executor.run_backtest(
            self.strategies, prepared_data
        )

        def make_factory(dfs):
            async def gen():
                for df in dfs:
                    yield df

            return gen

        return {symbol: make_factory(dfs) for symbol, dfs in results.items()}
