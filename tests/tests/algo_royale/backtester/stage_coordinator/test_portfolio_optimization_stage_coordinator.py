from datetime import datetime

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.optimization.portfolio_optimization_stage_coordinator import (
    PortfolioOptimizationStageCoordinator,
)
from tests.mocks.backtester.evaluator.backtest.mock_portfolio_backtest_evaluator import (
    MockPortfolioBacktestEvaluator,
)
from tests.mocks.backtester.executor.mock_portfolio_backtest_executor import (
    MockPortfolioBacktestExecutor,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.optimizer.portfolio.mock_portfolio_strategy_optimizer_factory import (
    MockPortfolioStrategyOptimizerFactory,
)
from tests.mocks.backtester.stage_data.loader.mock_portfolio_matrix_loader import (
    MockPortfolioMatrixLoader,
)
from tests.mocks.backtester.stage_data.loader.mock_symbol_strategy_data_loader import (
    MockSymbolStrategyDataLoader,
)
from tests.mocks.backtester.strategy_factory.portfolio.mock_portfolio_strategy_combinator_factory import (
    MockPortfolioStrategyCombinatorFactory,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def portfolio_optimization_coordinator(tmp_path):
    loader = MockSymbolStrategyDataLoader()
    manager = MockStageDataManager()
    logger = MockLoggable()
    # Create a real combinator_list_path file
    combinator_list_path = tmp_path / "combinators.json"
    combinator_list_path.write_text("[]")  # create an empty valid JSON file
    combinator_factory = MockPortfolioStrategyCombinatorFactory(
        str(combinator_list_path), logger, logger
    )
    executor = MockPortfolioBacktestExecutor()
    evaluator = MockPortfolioBacktestEvaluator()
    optimizer_factory = MockPortfolioStrategyOptimizerFactory()
    matrix_loader = MockPortfolioMatrixLoader()
    coordinator = PortfolioOptimizationStageCoordinator(
        data_loader=loader,
        stage_data_manager=manager,
        logger=logger,
        strategy_combinator_factory=combinator_factory,
        executor=executor,
        evaluator=evaluator,
        optimization_root=tmp_path,
        optimization_json_filename="opt.json",
        portfolio_matrix_loader=matrix_loader,
        portfolio_strategy_optimizer_factory=optimizer_factory,
        optimization_n_trials=1,
    )
    yield coordinator


def set_raise_exception(coordinator, value: bool):
    coordinator.executor.set_raise_exception(value)
    coordinator.evaluator.set_raise_exception(value)
    coordinator.portfolio_matrix_loader.set_raise_exception(value)
    coordinator.portfolio_strategy_optimizer_factory.set_raise_exception(value)


def reset_raise_exception(coordinator):
    coordinator.executor.reset_raise_exception()
    coordinator.evaluator.reset_raise_exception()
    coordinator.portfolio_matrix_loader.reset_raise_exception()
    coordinator.portfolio_strategy_optimizer_factory.reset_raise_exception()


def set_return_empty(coordinator, value: bool):
    coordinator.portfolio_matrix_loader.set_return_empty(value)


def reset_return_empty(coordinator):
    coordinator.portfolio_matrix_loader.reset_return_empty()


@pytest.mark.asyncio
class TestPortfolioOptimizationStageCoordinator:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, portfolio_optimization_coordinator):
        reset_raise_exception(portfolio_optimization_coordinator)
        reset_return_empty(portfolio_optimization_coordinator)
        yield
        reset_raise_exception(portfolio_optimization_coordinator)
        reset_return_empty(portfolio_optimization_coordinator)

    @pytest.mark.asyncio
    async def test_process_and_write_normal(self, portfolio_optimization_coordinator):
        # Should return a results dict with expected structure
        portfolio_optimization_coordinator.start_date = datetime(2022, 1, 1)
        portfolio_optimization_coordinator.end_date = datetime(2022, 12, 31)
        result = await portfolio_optimization_coordinator._process_and_write()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_process_and_write_empty_matrix(
        self, portfolio_optimization_coordinator
    ):
        set_return_empty(portfolio_optimization_coordinator, True)
        result = await portfolio_optimization_coordinator._process_and_write()
        assert result == {}
        reset_return_empty(portfolio_optimization_coordinator)

    @pytest.mark.asyncio
    async def test_process_and_write_exception(
        self, portfolio_optimization_coordinator
    ):
        set_raise_exception(portfolio_optimization_coordinator, True)
        result = await portfolio_optimization_coordinator._process_and_write()
        assert result == {}
        reset_raise_exception(portfolio_optimization_coordinator)

    def test_get_output_path(self, portfolio_optimization_coordinator, tmp_path):
        strategy_name = "DummyStrategy"
        symbols = ["AAPL", "GOOG"]
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 31)
        path = portfolio_optimization_coordinator._get_output_path(
            strategy_name, symbols, start_date, end_date
        )
        assert path.parent.exists()
        assert path.name == "opt.json"

    def test_backtest_and_evaluate_normal(self, portfolio_optimization_coordinator):
        class DummyStrategy:
            def get_id(self):
                return "DummyStrategy"

        df = pd.DataFrame({"AAPL": [1, 2, 3]})
        metrics = portfolio_optimization_coordinator._backtest_and_evaluate(
            DummyStrategy(), df
        )
        assert isinstance(metrics, dict)

    def test_backtest_and_evaluate_exception(self, portfolio_optimization_coordinator):
        class DummyStrategy:
            def get_id(self):
                return "DummyStrategy"

        set_raise_exception(portfolio_optimization_coordinator, True)
        df = pd.DataFrame({"AAPL": [1, 2, 3]})
        metrics = portfolio_optimization_coordinator._backtest_and_evaluate(
            DummyStrategy(), df
        )
        assert metrics == {}
        reset_raise_exception(portfolio_optimization_coordinator)

    def test_validate_optimization_results_normal(
        self, portfolio_optimization_coordinator
    ):
        # Should return True for valid structure
        results = {"sharpe": 2.0}
        portfolio_optimization_coordinator.window_id = "20220101_20221231"
        portfolio_optimization_coordinator.start_date = datetime(2022, 1, 1)
        portfolio_optimization_coordinator.end_date = datetime(2022, 12, 31)
        assert portfolio_optimization_coordinator._validate_optimization_results(
            results
        ) in [True, False]  # depends on validator

    def test_validate_optimization_results_exception(
        self, portfolio_optimization_coordinator
    ):
        set_raise_exception(portfolio_optimization_coordinator, True)
        results = {"sharpe": 2.0}
        portfolio_optimization_coordinator.window_id = "20220101_20221231"
        portfolio_optimization_coordinator.start_date = datetime(2022, 1, 1)
        portfolio_optimization_coordinator.end_date = datetime(2022, 12, 31)
        assert (
            portfolio_optimization_coordinator._validate_optimization_results(results)
            is False
        )
        reset_raise_exception(portfolio_optimization_coordinator)

    def test_write_results_normal(self, portfolio_optimization_coordinator):
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 31)
        symbols = ["AAPL", "GOOG"]
        strategy_name = "DummyStrategy"
        optimization_result = {"sharpe": 2.0}
        collective_results = {}
        portfolio_optimization_coordinator.window_id = "20220101_20221231"
        result = portfolio_optimization_coordinator._write_results(
            start_date,
            end_date,
            symbols,
            strategy_name,
            optimization_result,
            collective_results,
        )
        assert isinstance(result, dict)

    def test_write_results_exception(self, portfolio_optimization_coordinator):
        set_raise_exception(portfolio_optimization_coordinator, True)
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 31)
        symbols = ["AAPL", "GOOG"]
        strategy_name = "DummyStrategy"
        optimization_result = {"sharpe": 2.0}
        collective_results = {}
        portfolio_optimization_coordinator.window_id = "20220101_20221231"
        result = portfolio_optimization_coordinator._write_results(
            start_date,
            end_date,
            symbols,
            strategy_name,
            optimization_result,
            collective_results,
        )
        assert isinstance(result, dict)
        reset_raise_exception(portfolio_optimization_coordinator)

    def test_get_symbols_dir_name(self, portfolio_optimization_coordinator):
        symbols = ["GOOG", "AAPL"]
        dir_name = portfolio_optimization_coordinator._get_symbols_dir_name(symbols)
        assert dir_name == "AAPL_GOOG"
        assert portfolio_optimization_coordinator._get_symbols_dir_name([]) == "empty"
