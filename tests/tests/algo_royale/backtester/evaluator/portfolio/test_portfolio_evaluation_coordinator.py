import pytest

from algo_royale.backtester.evaluator.portfolio.portfolio_evaluation_coordinator import (
    PortfolioEvaluationCoordinator,
)
from tests.mocks.backtester.evaluator.portfolio.mock_portfolio_cross_strategy_summary import (
    MockPortfolioCrossStrategySummary,
)
from tests.mocks.backtester.evaluator.portfolio.mock_portfolio_cross_window_evaluator import (
    MockPortfolioCrossWindowEvaluator,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def coordinator(tmp_path):
    cross_window = MockPortfolioCrossWindowEvaluator()
    cross_strategy = MockPortfolioCrossStrategySummary()
    logger = MockLoggable()
    # Create symbol/strategy dirs
    symbol_dir = tmp_path / "SYM1"
    symbol_dir.mkdir()
    strat_dir = symbol_dir / "STRAT1"
    strat_dir.mkdir()
    return (
        PortfolioEvaluationCoordinator(
            logger=logger,
            cross_window_evaluator=cross_window,
            cross_strategy_summary=cross_strategy,
            optimization_root=str(tmp_path),
        ),
        cross_window,
        cross_strategy,
        symbol_dir,
        strat_dir,
    )


def test_run_calls_evaluators(coordinator):
    coordinator_obj, cross_window, cross_strategy, symbol_dir, strat_dir = coordinator
    coordinator_obj.run()
    assert cross_window.run_called
    assert cross_strategy.run_called


def test_run_handles_cross_window_exception(coordinator):
    coordinator_obj, cross_window, cross_strategy, symbol_dir, strat_dir = coordinator
    cross_window.set_raise_exception(True)
    with pytest.raises(RuntimeError):
        coordinator_obj.run()


def test_run_handles_cross_strategy_exception(coordinator):
    coordinator_obj, cross_window, cross_strategy, symbol_dir, strat_dir = coordinator
    cross_strategy.set_raise_exception(True)
    with pytest.raises(RuntimeError):
        coordinator_obj.run()
