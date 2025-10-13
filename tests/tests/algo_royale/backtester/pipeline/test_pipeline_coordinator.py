import pytest

from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from tests.mocks.backtester.evaluator.portfolio.mock_portfolio_evaluation_coordinator import (
    MockPortfolioEvaluationCoordinator,
)
from tests.mocks.backtester.evaluator.strategy.mock_signal_strategy_evaluation_coordinator import (
    MockSignalStrategyEvaluationCoordinator,
)
from tests.mocks.backtester.evaluator.symbol.mock_symbol_evaluation_coordinator import (
    MockSymbolEvaluationCoordinator,
)
from tests.mocks.backtester.walkforward.mock_walk_forward_coordinator import (
    MockWalkForwardCoordinator,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.mark.asyncio
class TestPipelineCoordinator:
    def setup_method(self):
        self.logger = MockLoggable()
        self.signal_strategy_walk_forward = MockWalkForwardCoordinator()
        self.portfolio_walk_forward = MockWalkForwardCoordinator()
        self.signal_strategy_eval = MockSignalStrategyEvaluationCoordinator()
        self.symbol_eval = MockSymbolEvaluationCoordinator()
        self.portfolio_eval = MockPortfolioEvaluationCoordinator()
        self.coordinator = PipelineCoordinator(
            signal_strategy_walk_forward_coordinator=self.signal_strategy_walk_forward,
            portfolio_walk_forward_coordinator=self.portfolio_walk_forward,
            signal_strategy_evaluation_coordinator=self.signal_strategy_eval,
            symbol_evaluation_coordinator=self.symbol_eval,
            portfolio_evaluation_coordinator=self.portfolio_eval,
            logger=self.logger,
        )

    async def test_run_async_success(self):
        result = await self.coordinator.run_async()
        assert result is True
        assert self.signal_strategy_walk_forward.run_async_called
        assert self.portfolio_walk_forward.run_async_called
        assert self.signal_strategy_eval.run_called
        assert self.symbol_eval.run_called
        assert self.portfolio_eval.run_called

    async def test_run_async_pipeline_exception(self):
        self.signal_strategy_walk_forward.set_raise(True)
        result = await self.coordinator.run_async()
        assert result is False

    async def test_run_async_portfolio_walk_forward_exception(self):
        self.portfolio_walk_forward.set_raise(True)
        result = await self.coordinator.run_async()
        assert result is False

    async def test_run_async_signal_strategy_eval_exception(self):
        self.signal_strategy_eval.set_raise(True)
        result = await self.coordinator.run_async()
        assert result is False

    async def test_run_async_symbol_eval_exception(self):
        self.symbol_eval.set_raise(True)
        result = await self.coordinator.run_async()
        assert result is False

    async def test_run_async_portfolio_eval_exception(self):
        self.portfolio_eval.set_raise(True)
        result = await self.coordinator.run_async()
        assert result is False

    def test_run_sync_success(self):
        result = self.coordinator.run()
        assert result is True
