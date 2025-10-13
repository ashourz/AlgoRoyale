from datetime import datetime

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.testing.signal_strategy_testing_stage_coordinator import (
    SignalStrategyTestingStageCoordinator,
)
from tests.mocks.backtester.evaluator.backtest.mock_signal_backtest_evaluator import (
    MockSignalBacktestEvaluator,
)
from tests.mocks.backtester.executor.mock_strategy_backtest_executor import (
    MockStrategyBacktestExecutor,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.stage_data.loader.mock_symbol_strategy_data_loader import (
    MockSymbolStrategyDataLoader,
)
from tests.mocks.backtester.strategy_factory.signal.mock_signal_strategy_combinator_factory import (
    MockSignalStrategyCombinatorFactory,
)
from tests.mocks.backtester.strategy_factory.signal.mock_signal_strategy_factory import (
    MockSignalStrategyFactory,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def signal_strategy_testing_coordinator(tmp_path):
    loader = MockSymbolStrategyDataLoader()
    manager = MockStageDataManager()
    logger = MockLoggable()
    combinator_list_path = tmp_path / "combinators.json"
    combinator_list_path.write_text("[]")
    combinator_factory = MockSignalStrategyCombinatorFactory(
        str(combinator_list_path), logger, logger
    )
    executor = MockStrategyBacktestExecutor()
    evaluator = MockSignalBacktestEvaluator()
    strategy_factory = MockSignalStrategyFactory()
    coordinator = SignalStrategyTestingStageCoordinator(
        data_loader=loader,
        stage_data_manager=manager,
        strategy_executor=executor,
        strategy_evaluator=evaluator,
        strategy_factory=strategy_factory,
        logger=logger,
        strategy_combinator_factory=combinator_factory,
        optimization_root=tmp_path,
        optimization_json_filename="test_opt.json",
    )
    yield coordinator


def set_raise_exception(coordinator, value: bool):
    coordinator.executor.set_raise_exception(value)
    coordinator.evaluator.set_raise_exception(value)
    coordinator.strategy_factory.set_raise_exception(value)


def reset_raise_exception(coordinator):
    coordinator.executor.reset_raise_exception()
    coordinator.evaluator.reset_raise_exception()
    coordinator.strategy_factory.reset_raise_exception()


@pytest.mark.asyncio
class TestSignalStrategyTestingStageCoordinator:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, signal_strategy_testing_coordinator):
        reset_raise_exception(signal_strategy_testing_coordinator)
        yield
        reset_raise_exception(signal_strategy_testing_coordinator)

    @pytest.mark.asyncio
    async def test_process_and_write_normal(self, signal_strategy_testing_coordinator):
        signal_strategy_testing_coordinator.test_start_date = datetime(2022, 7, 1)
        signal_strategy_testing_coordinator.test_end_date = datetime(2022, 12, 31)
        signal_strategy_testing_coordinator.test_window_id = "20220701_20221231"

        async def df_iter():
            yield pd.DataFrame({"AAPL": [1, 2, 3]})

        data = {"AAPL": lambda: df_iter()}
        result = await signal_strategy_testing_coordinator._process_and_write(data)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_process_and_write_exception(
        self, signal_strategy_testing_coordinator
    ):
        set_raise_exception(signal_strategy_testing_coordinator, True)
        signal_strategy_testing_coordinator.test_start_date = datetime(2022, 7, 1)
        signal_strategy_testing_coordinator.test_end_date = datetime(2022, 12, 31)
        signal_strategy_testing_coordinator.test_window_id = "20220701_20221231"

        async def df_iter():
            yield pd.DataFrame({"AAPL": [1, 2, 3]})

        data = {"AAPL": lambda: df_iter()}
        try:
            result = await signal_strategy_testing_coordinator._process_and_write(data)
        except Exception as e:
            assert "Mocked exception" in str(e)
            reset_raise_exception(signal_strategy_testing_coordinator)
            return
        assert isinstance(result, dict)
        reset_raise_exception(signal_strategy_testing_coordinator)

    def test_get_train_optimization_results_normal(
        self, signal_strategy_testing_coordinator
    ):
        symbol = "AAPL"
        strategy_name = "DummyStrategy"
        signal_strategy_testing_coordinator.train_window_id = "20220101_20220630"

        def fake_get_optimization_results(*a, **kw):
            return {"20220101_20220630": {"optimization": {"best_params": {"foo": 1}}}}

        signal_strategy_testing_coordinator._get_optimization_results = (
            fake_get_optimization_results
        )
        results = signal_strategy_testing_coordinator._get_train_optimization_results(
            strategy_name, symbol, "2022-01-01", "2022-06-30"
        )
        assert isinstance(results, dict)

    def test_get_train_optimization_results_exception(
        self, signal_strategy_testing_coordinator
    ):
        symbol = "AAPL"
        strategy_name = "DummyStrategy"
        signal_strategy_testing_coordinator.train_window_id = "20220101_20220630"

        def fake_get_optimization_results(*a, **kw):
            raise Exception("fail")

        signal_strategy_testing_coordinator._get_optimization_results = (
            fake_get_optimization_results
        )
        results = signal_strategy_testing_coordinator._get_train_optimization_results(
            strategy_name, symbol, "2022-01-01", "2022-06-30"
        )
        assert results is None

    def test_get_test_optimization_results_normal(
        self, signal_strategy_testing_coordinator
    ):
        symbol = "AAPL"
        strategy_name = "DummyStrategy"
        signal_strategy_testing_coordinator.test_window_id = "20220701_20221231"

        def fake_get_optimization_results(*a, **kw):
            return {"20220701_20221231": {"optimization": {"best_params": {"foo": 1}}}}

        signal_strategy_testing_coordinator._get_optimization_results = (
            fake_get_optimization_results
        )
        results = signal_strategy_testing_coordinator._get_test_optimization_results(
            strategy_name, symbol, "2022-07-01", "2022-12-31"
        )
        assert isinstance(results, dict)

    def test_get_test_optimization_results_exception(
        self, signal_strategy_testing_coordinator
    ):
        symbol = "AAPL"
        strategy_name = "DummyStrategy"
        signal_strategy_testing_coordinator.test_window_id = "20220701_20221231"

        def fake_get_optimization_results(*a, **kw):
            raise Exception("fail")

        signal_strategy_testing_coordinator._get_optimization_results = (
            fake_get_optimization_results
        )
        results = signal_strategy_testing_coordinator._get_test_optimization_results(
            strategy_name, symbol, "2022-07-01", "2022-12-31"
        )
        assert results is None
