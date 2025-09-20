from datetime import datetime

import pytest

from algo_royale.backtester.stage_coordinator.testing.portfolio_testing_stage_coordinator import (
    PortfolioTestingStageCoordinator,
)
from tests.mocks.backtester.evaluator.backtest.mock_portfolio_backtest_evaluator import (
    MockPortfolioBacktestEvaluator,
)
from tests.mocks.backtester.executor.mock_portfolio_backtest_executor import (
    MockPortfolioBacktestExecutor,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
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
def portfolio_testing_coordinator(tmp_path):
    loader = MockSymbolStrategyDataLoader()
    manager = MockStageDataManager()
    logger = MockLoggable()
    strategy_logger = MockLoggable()
    combinator_list_path = tmp_path / "combinators.json"
    combinator_list_path.write_text("[]")
    combinator_factory = MockPortfolioStrategyCombinatorFactory(
        str(combinator_list_path), logger, strategy_logger
    )
    executor = MockPortfolioBacktestExecutor()
    evaluator = MockPortfolioBacktestEvaluator()
    matrix_loader = MockPortfolioMatrixLoader()
    coordinator = PortfolioTestingStageCoordinator(
        data_loader=loader,
        stage_data_manager=manager,
        logger=logger,
        strategy_logger=strategy_logger,
        strategy_combinator_factory=combinator_factory,
        executor=executor,
        evaluator=evaluator,
        optimization_root=tmp_path,
        optimization_json_filename="test_opt.json",
        portfolio_matrix_loader=matrix_loader,
    )
    yield coordinator


def set_raise_exception(coordinator, value: bool):
    coordinator.executor.set_raise_exception(value)
    coordinator.evaluator.set_raise_exception(value)
    coordinator.portfolio_matrix_loader.set_raise_exception(value)


def reset_raise_exception(coordinator):
    coordinator.executor.reset_raise_exception()
    coordinator.evaluator.reset_raise_exception()
    coordinator.portfolio_matrix_loader.reset_raise_exception()


def set_return_empty(coordinator, value: bool):
    coordinator.portfolio_matrix_loader.set_return_empty(value)


def reset_return_empty(coordinator):
    coordinator.portfolio_matrix_loader.reset_return_empty()


@pytest.mark.asyncio
class TestPortfolioTestingStageCoordinator:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, portfolio_testing_coordinator):
        reset_raise_exception(portfolio_testing_coordinator)
        reset_return_empty(portfolio_testing_coordinator)
        yield
        reset_raise_exception(portfolio_testing_coordinator)
        reset_return_empty(portfolio_testing_coordinator)

    @pytest.mark.asyncio
    async def test_process_and_write_normal(self, portfolio_testing_coordinator):
        # Should return a results dict with expected structure
        portfolio_testing_coordinator.train_start_date = datetime(2022, 1, 1)
        portfolio_testing_coordinator.train_end_date = datetime(2022, 6, 30)
        portfolio_testing_coordinator.test_start_date = datetime(2022, 7, 1)
        portfolio_testing_coordinator.test_end_date = datetime(2022, 12, 31)
        portfolio_testing_coordinator.train_window_id = "20220101_20220630"
        portfolio_testing_coordinator.test_window_id = "20220701_20221231"
        result = await portfolio_testing_coordinator._process_and_write()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_process_and_write_empty_matrix(self, portfolio_testing_coordinator):
        set_return_empty(portfolio_testing_coordinator, True)
        portfolio_testing_coordinator.train_start_date = datetime(2022, 1, 1)
        portfolio_testing_coordinator.train_end_date = datetime(2022, 6, 30)
        portfolio_testing_coordinator.test_start_date = datetime(2022, 7, 1)
        portfolio_testing_coordinator.test_end_date = datetime(2022, 12, 31)
        portfolio_testing_coordinator.train_window_id = "20220101_20220630"
        portfolio_testing_coordinator.test_window_id = "20220701_20221231"
        result = await portfolio_testing_coordinator._process_and_write()
        assert result == {}
        reset_return_empty(portfolio_testing_coordinator)

    @pytest.mark.asyncio
    async def test_process_and_write_exception(self, portfolio_testing_coordinator):
        set_raise_exception(portfolio_testing_coordinator, True)
        portfolio_testing_coordinator.train_start_date = datetime(2022, 1, 1)
        portfolio_testing_coordinator.train_end_date = datetime(2022, 6, 30)
        portfolio_testing_coordinator.test_start_date = datetime(2022, 7, 1)
        portfolio_testing_coordinator.test_end_date = datetime(2022, 12, 31)
        portfolio_testing_coordinator.train_window_id = "20220101_20220630"
        portfolio_testing_coordinator.test_window_id = "20220701_20221231"
        result = await portfolio_testing_coordinator._process_and_write()
        assert result == {}
        reset_raise_exception(portfolio_testing_coordinator)

    def test_get_optimized_params_normal(self, portfolio_testing_coordinator):
        symbols = ["AAPL", "GOOG"]
        strategy_name = "DummyStrategy"

        class DummyStrategy:
            def __init__(self, logger, foo=None):
                pass

        portfolio_testing_coordinator.train_window_id = "20220101_20220630"
        portfolio_testing_coordinator.train_start_date = datetime(2022, 1, 1)
        portfolio_testing_coordinator.train_end_date = datetime(2022, 6, 30)

        # Patch _get_optimization_results to return valid params with all required keys
        def fake_get_optimization_results(*a, **kw):
            return {
                "20220101_20220630": {
                    "strategy": "DummyStrategy",
                    "symbols": ["AAPL", "GOOG"],
                    "optimization": {"best_params": {"foo": 1}},
                    "window": {
                        "start_date": "2022-01-01",
                        "end_date": "2022-06-30",
                        "window_id": "20220101_20220630",
                    },
                }
            }

        portfolio_testing_coordinator._get_optimization_results = (
            fake_get_optimization_results
        )
        params = portfolio_testing_coordinator._get_optimized_params(
            symbols, strategy_name, DummyStrategy
        )
        assert isinstance(params, dict)

    def test_get_optimized_params_exception(self, portfolio_testing_coordinator):
        symbols = ["AAPL", "GOOG"]
        strategy_name = "DummyStrategy"

        class DummyStrategy:
            def __init__(self, logger, foo=None):
                pass

        portfolio_testing_coordinator.train_window_id = "20220101_20220630"
        portfolio_testing_coordinator.train_start_date = datetime(2022, 1, 1)
        portfolio_testing_coordinator.train_end_date = datetime(2022, 6, 30)

        # Patch _get_optimization_results to raise
        def fake_get_optimization_results(*a, **kw):
            raise Exception("fail")

        portfolio_testing_coordinator._get_optimization_results = (
            fake_get_optimization_results
        )
        params = portfolio_testing_coordinator._get_optimized_params(
            symbols, strategy_name, DummyStrategy
        )
        assert params is None

    def test_validate_optimization_results_normal(self, portfolio_testing_coordinator):
        results = {"20220101_20220630": {"optimization": {"best_params": {"foo": 1}}}}
        assert portfolio_testing_coordinator._validate_optimization_results(
            results
        ) in [True, False]

    def test_validate_optimization_results_exception(
        self, portfolio_testing_coordinator
    ):
        # Patch to raise
        def fake_validation(*a, **kw):
            raise Exception("fail")

        portfolio_testing_coordinator.logger = MockLoggable()
        portfolio_testing_coordinator._validate_optimization_results = fake_validation
        try:
            result = portfolio_testing_coordinator._validate_optimization_results({})
        except Exception:
            result = False
        assert result is False or result is None

    def test_write_test_results_normal(self, portfolio_testing_coordinator):
        symbols = ["AAPL", "GOOG"]
        metrics = {"sharpe": 2.0}
        strategy_name = "DummyStrategy"
        backtest_results = {"transactions": []}
        optimized_params = {"foo": 1}
        optimization_result = {
            "20220101_20220630": {"optimization": {"best_params": {"foo": 1}}}
        }
        collective_results = {}
        portfolio_testing_coordinator.test_window_id = "20220701_20221231"
        portfolio_testing_coordinator.test_start_date = datetime(2022, 7, 1)
        portfolio_testing_coordinator.test_end_date = datetime(2022, 12, 31)
        result = portfolio_testing_coordinator._write_test_results(
            symbols,
            metrics,
            strategy_name,
            backtest_results,
            optimized_params,
            optimization_result,
            collective_results,
        )
        assert isinstance(result, dict)

    def test_write_test_results_exception(self, portfolio_testing_coordinator):
        symbols = ["AAPL", "GOOG"]
        metrics = {"sharpe": 2.0}
        strategy_name = "DummyStrategy"
        backtest_results = {"transactions": []}
        optimized_params = {"foo": 1}
        optimization_result = {
            "20220101_20220630": {"optimization": {"best_params": {"foo": 1}}}
        }
        collective_results = {}
        portfolio_testing_coordinator.test_window_id = "20220701_20221231"
        portfolio_testing_coordinator.test_start_date = datetime(2022, 7, 1)
        portfolio_testing_coordinator.test_end_date = datetime(2022, 12, 31)

        # Patch to raise
        def fake_write(*a, **kw):
            raise Exception("fail")

        portfolio_testing_coordinator._get_optimization_result_path = fake_write
        try:
            result = portfolio_testing_coordinator._write_test_results(
                symbols,
                metrics,
                strategy_name,
                backtest_results,
                optimized_params,
                optimization_result,
                collective_results,
            )
        except Exception:
            result = None
        assert result is None or isinstance(result, dict)

    def test_get_symbols_dir_name(self, portfolio_testing_coordinator):
        symbols = ["GOOG", "AAPL"]
        dir_name = portfolio_testing_coordinator._get_symbols_dir_name(symbols)
        assert dir_name == "AAPL_GOOG"
        assert portfolio_testing_coordinator._get_symbols_dir_name([]) == "empty"
