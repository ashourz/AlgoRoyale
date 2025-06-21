import json
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.portfolio.optimizer.portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.optimizer.portfolio_strategy_optimizer import (
    PortfolioStrategyOptimizer,
)
from algo_royale.portfolio.strategies.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class PortfolioOptimizationStageCoordinator(StageCoordinator):
    """
    Coordinator for the portfolio optimization stage of the backtest pipeline.
    Optimizes portfolio strategies for a list of symbols using the provided data loader, data preparer, data writer, and optimizer.
    """

    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        strategy_combinators: Optional[
            Sequence[type[PortfolioStrategyCombinator]]
        ] = None,
    ):
        super().__init__(
            stage=BacktestStage.OPTIMIZATION,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.strategy_combinators = strategy_combinators
        if not self.strategy_combinators:
            raise ValueError("No portfolio strategy combinators provided")

    async def process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[str, dict]]:
        """Process the portfolio optimization stage."""
        results = {}
        for symbol, df_iter_factory in prepared_data.items():
            if symbol not in prepared_data:
                self.logger.warning(f"No prepared data for symbol: {symbol}")
                continue
            dfs = []
            async for df in df_iter_factory():
                dfs.append(df)
            if not dfs:
                self.logger.warning(
                    f"No data for symbol: {symbol} in window {self.window_id}"
                )
                continue
            train_df = pd.concat(dfs, ignore_index=True)
            for strategy_combinator in self.strategy_combinators:
                for strat_factory in strategy_combinator.all_strategy_combinations():
                    strategy_class = (
                        strat_factory.func
                        if hasattr(strat_factory, "func")
                        else strat_factory
                    )
                    strategy_name = (
                        strategy_class.__name__
                        if hasattr(strategy_class, "__name__")
                        else str(strategy_class)
                    )
                    try:
                        optimizer = PortfolioStrategyOptimizer(
                            strategy_class=strategy_class,
                            backtest_fn=lambda strat, df_: self._backtest_and_evaluate(
                                symbol, strat, df_
                            ),
                            logger=self.logger,
                        )
                        optimization_result = optimizer.optimize(symbol, train_df)
                    except Exception as e:
                        self.logger.error(
                            f"Portfolio optimization failed for symbol {symbol}, strategy {strategy_name}: {e}"
                        )
                        continue
                    out_dir = self.stage_data_manager.get_directory_path(
                        BacktestStage.OPTIMIZATION,
                        strategy_name,
                        symbol,
                        self.start_date,
                        self.end_date,
                    )
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_path = out_dir / "portfolio_optimization_result.json"
                    self.logger.info(
                        f"Saving portfolio optimization results for {symbol} {strategy_name} to {out_path}"
                    )
                    if out_path.exists():
                        with open(out_path, "r") as f:
                            opt_results = json.load(f)
                    else:
                        opt_results = {}
                    if self.window_id not in opt_results:
                        opt_results[self.window_id] = {}
                    opt_results[self.window_id]["optimization"] = optimization_result
                    opt_results[self.window_id]["window"] = {
                        "start_date": str(self.start_date),
                        "end_date": str(self.end_date),
                    }
                    with open(out_path, "w") as f:
                        json.dump(opt_results, f, indent=2, default=str)
                    results.setdefault(symbol, {})[strategy_name] = {
                        self.window_id: optimization_result
                    }
        return results

    async def _backtest_and_evaluate(
        self, symbol: str, strategy: BasePortfolioStrategy, df: pd.DataFrame
    ):
        async def data_factory():
            yield df

        # This should call your portfolio backtest executor and evaluator
        # Placeholder: return empty dict
        return {}

    async def _write(self, stage, processed_data):
        # No-op: writing is handled in process()
        pass
