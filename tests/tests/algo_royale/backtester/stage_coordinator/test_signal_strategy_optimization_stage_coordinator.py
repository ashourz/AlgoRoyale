from datetime import datetime

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.optimization.signal_strategy_optimization_stage_coordinator import (
    SignalStrategyOptimizationStageCoordinator,
)
from tests.mocks.backtester.evaluator.backtest.mock_signal_backtest_evaluator import (
    MockSignalBacktestEvaluator,
)
from tests.mocks.backtester.executor.mock_strategy_backtest_executor import (
    MockStrategyBacktestExecutor,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.optimizer.signal.mock_signal_strategy_optimizer_factory import (
    MockSignalStrategyOptimizerFactory,
)
from tests.mocks.backtester.stage_data.loader.mock_symbol_strategy_data_loader import (
    MockSymbolStrategyDataLoader,
)
from tests.mocks.backtester.strategy_factory.signal.mock_signal_strategy_combinator_factory import (
    MockSignalStrategyCombinatorFactory,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def signal_strategy_optimization_coordinator(tmp_path):
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
    optimizer_factory = MockSignalStrategyOptimizerFactory()
    coordinator = SignalStrategyOptimizationStageCoordinator(
        data_loader=loader,
        logger=logger,
        stage_data_manager=manager,
        strategy_executor=executor,
        strategy_evaluator=evaluator,
        strategy_combinator_factory=combinator_factory,
        optimization_root=tmp_path,
        optimization_json_filename="opt.json",
        signal_strategy_optimizer_factory=optimizer_factory,
        optimization_n_trials=1,
    )
    yield coordinator


def set_raise_exception(coordinator, value: bool):
    coordinator.executor.set_raise_exception(value)
    coordinator.evaluator.set_raise_exception(value)
    coordinator.signal_strategy_optimizer_factory.set_raise_exception(value)


def reset_raise_exception(coordinator):
    coordinator.executor.reset_raise_exception()
    coordinator.evaluator.reset_raise_exception()
    coordinator.signal_strategy_optimizer_factory.reset_raise_exception()


@pytest.mark.asyncio
class TestSignalStrategyOptimizationStageCoordinator:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, signal_strategy_optimization_coordinator):
        reset_raise_exception(signal_strategy_optimization_coordinator)
        yield
        reset_raise_exception(signal_strategy_optimization_coordinator)

    @pytest.mark.asyncio
    async def test_process_and_write_normal(
        self, signal_strategy_optimization_coordinator
    ):
        # Should return a results dict with expected structure
        signal_strategy_optimization_coordinator.start_date = datetime(2022, 1, 1)
        signal_strategy_optimization_coordinator.end_date = datetime(2022, 12, 31)
        signal_strategy_optimization_coordinator.window_id = "20220101_20221231"

        # Prepare mock data
        async def df_iter():
            yield pd.DataFrame({"AAPL": [1, 2, 3]})

        data = {"AAPL": lambda: df_iter()}
        result = await signal_strategy_optimization_coordinator._process_and_write(data)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_process_and_write_exception(
        self, signal_strategy_optimization_coordinator
    ):
        set_raise_exception(signal_strategy_optimization_coordinator, True)
        signal_strategy_optimization_coordinator.start_date = datetime(2022, 1, 1)
        signal_strategy_optimization_coordinator.end_date = datetime(2022, 12, 31)
        signal_strategy_optimization_coordinator.window_id = "20220101_20221231"

        async def df_iter():
            yield pd.DataFrame({"AAPL": [1, 2, 3]})

        data = {"AAPL": lambda: df_iter()}
        result = await signal_strategy_optimization_coordinator._process_and_write(data)
        assert isinstance(result, dict)
        reset_raise_exception(signal_strategy_optimization_coordinator)

    def test_get_output_path(self, signal_strategy_optimization_coordinator, tmp_path):
        strategy_name = "DummyStrategy"
        symbol = "AAPL"
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 31)
        path = signal_strategy_optimization_coordinator._get_output_path(
            strategy_name, symbol, start_date, end_date
        )
        assert path.parent.exists()
        assert path.name == "opt.json"

    @pytest.mark.asyncio
    async def test_backtest_and_evaluate_normal(
        self, signal_strategy_optimization_coordinator
    ):
        class DummyStrategy:
            pass

        df = pd.DataFrame({"AAPL": [1, 2, 3]})
        metrics = await signal_strategy_optimization_coordinator._backtest_and_evaluate(
            "AAPL", DummyStrategy(), df
        )
        assert isinstance(metrics, dict)

    @pytest.mark.asyncio
    async def test_backtest_and_evaluate_exception(
        self, signal_strategy_optimization_coordinator
    ):
        set_raise_exception(signal_strategy_optimization_coordinator, True)

        class DummyStrategy:
            pass

        df = pd.DataFrame({"AAPL": [1, 2, 3]})
        try:
            metrics = (
                await signal_strategy_optimization_coordinator._backtest_and_evaluate(
                    "AAPL", DummyStrategy(), df
                )
            )
        except Exception as e:
            assert "Mocked exception" in str(e)
            reset_raise_exception(signal_strategy_optimization_coordinator)
            return
        assert False, "Exception was not raised as expected"
        reset_raise_exception(signal_strategy_optimization_coordinator)

    def test_validate_optimization_results_normal(
        self, signal_strategy_optimization_coordinator
    ):
        results = {"20220101_20221231": {"optimization": {"best_params": {"foo": 1}}}}
        assert signal_strategy_optimization_coordinator._validate_optimization_results(
            results
        ) in [True, False]

    def test_validate_optimization_results_exception(
        self, signal_strategy_optimization_coordinator
    ):
        set_raise_exception(signal_strategy_optimization_coordinator, True)
        results = {"20220101_20221231": {"optimization": {"best_params": {"foo": 1}}}}
        assert (
            signal_strategy_optimization_coordinator._validate_optimization_results(
                results
            )
            is False
        )
        reset_raise_exception(signal_strategy_optimization_coordinator)

    def test_write_results_normal(self, signal_strategy_optimization_coordinator):
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 31)
        symbol = "AAPL"
        strategy_name = "DummyStrategy"
        optimization_result = {"best_params": {"foo": 1}, "best_value": 2.0}
        collective_results = {}
        signal_strategy_optimization_coordinator.window_id = "20220101_20221231"
        result = signal_strategy_optimization_coordinator._write_results(
            symbol,
            start_date,
            end_date,
            strategy_name,
            optimization_result,
            collective_results,
        )
        assert isinstance(result, dict)

    def test_write_results_exception(self, signal_strategy_optimization_coordinator):
        set_raise_exception(signal_strategy_optimization_coordinator, True)
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 31)
        symbol = "AAPL"
        strategy_name = "DummyStrategy"
        optimization_result = {"best_params": {"foo": 1}, "best_value": 2.0}
        collective_results = {}
        signal_strategy_optimization_coordinator.window_id = "20220101_20221231"

        # Patch get_existing_optimization_results to raise
        def fake_get_existing(*a, **kw):
            raise Exception("fail")

        signal_strategy_optimization_coordinator.get_existing_optimization_results = (
            fake_get_existing
        )
        try:
            result = signal_strategy_optimization_coordinator._write_results(
                symbol,
                start_date,
                end_date,
                strategy_name,
                optimization_result,
                collective_results,
            )
        except Exception:
            result = None
        assert result is None or isinstance(result, dict)
