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
def mock_loader():
    return MockSymbolStrategyDataLoader()


@pytest.fixture
def mock_logger():
    return MockLoggable()


@pytest.fixture
def mock_stage_data_manager():
    return MockStageDataManager()


@pytest.fixture
def mock_strategy_executor():
    return MockStrategyBacktestExecutor()


@pytest.fixture
def mock_strategy_evaluator():
    return MockSignalBacktestEvaluator()


@pytest.fixture
def mock_strategy_combinator_factory():
    return MockSignalStrategyCombinatorFactory()


@pytest.fixture
def mock_optimizer_factory():
    return MockSignalStrategyOptimizerFactory()


def test_init_success(
    mock_loader,
    mock_logger,
    mock_stage_data_manager,
    mock_strategy_executor,
    mock_strategy_evaluator,
    mock_strategy_combinator_factory,
    mock_optimizer_factory,
):
    # Should not raise
    SignalStrategyOptimizationStageCoordinator(
        data_loader=mock_loader,
        logger=mock_logger,
        stage_data_manager=mock_stage_data_manager,
        strategy_executor=mock_strategy_executor,
        strategy_evaluator=mock_strategy_evaluator,
        strategy_combinator_factory=mock_strategy_combinator_factory,
        optimization_root="/tmp",
        optimization_json_filename="opt.json",
        signal_strategy_optimizer_factory=mock_optimizer_factory,
        optimization_n_trials=1,
    )


def test_init_invalid_optimization_root(
    mock_loader,
    mock_logger,
    mock_stage_data_manager,
    mock_strategy_executor,
    mock_strategy_evaluator,
    mock_strategy_combinator_factory,
    mock_optimizer_factory,
):
    # Should raise if optimization_root is not a directory
    with pytest.raises(Exception):
        SignalStrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            logger=mock_logger,
            stage_data_manager=mock_stage_data_manager,
            strategy_executor=mock_strategy_executor,
            strategy_evaluator=mock_strategy_evaluator,
            strategy_combinator_factory=mock_strategy_combinator_factory,
            optimization_root="/not/a/real/dir",
            optimization_json_filename="opt.json",
            signal_strategy_optimizer_factory=mock_optimizer_factory,
            optimization_n_trials=1,
        )


# Add more tests for run() and any other public methods, including error/exception handling, as needed.
