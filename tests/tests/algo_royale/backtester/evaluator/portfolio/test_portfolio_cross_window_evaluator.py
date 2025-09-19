import json

import pytest

from algo_royale.backtester.evaluator.portfolio.portfolio_cross_window_evaluator import (
    PortfolioCrossWindowEvaluator,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def evaluator():
    return PortfolioCrossWindowEvaluator(
        logger=MockLoggable(), window_json_filename="window_result.json"
    )


def create_window_dir(tmp_path, window_data):
    window_dir = tmp_path / "window1"
    window_dir.mkdir()
    with open(window_dir / "window_result.json", "w") as f:
        json.dump(window_data, f)
    return window_dir


def test_run_valid(tmp_path, evaluator):
    strategy_dir = tmp_path / "strategy1"
    strategy_dir.mkdir()
    # window_result.json with valid structure
    window_data = {
        "w1": {
            "optimization": {
                "metrics": {"total_return": 1.0, "sharpe": 2.0},
                "best_params": {"param1": 5},
                "entry_conditions": [1],
            }
        }
    }
    create_window_dir(strategy_dir, window_data)
    result = evaluator.run(strategy_dir)
    assert result is not None
    assert "summary" in result
    assert result["n_windows"] == 1


def test_run_missing_file(tmp_path, evaluator):
    strategy_dir = tmp_path / "strategy2"
    strategy_dir.mkdir()
    # No window_result.json
    (strategy_dir / "window1").mkdir()
    result = evaluator.run(strategy_dir)
    assert result is None


def test_run_invalid_json(tmp_path, evaluator):
    strategy_dir = tmp_path / "strategy3"
    strategy_dir.mkdir()
    window_dir = strategy_dir / "window1"
    window_dir.mkdir()
    # Write invalid JSON
    with open(window_dir / "window_result.json", "w") as f:
        f.write("not a json")
    # Should skip invalid file and return None
    result = evaluator.run(strategy_dir)
    assert result is None


def test_run_not_a_dir(tmp_path, evaluator):
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("test")
    result = evaluator.run(file_path)
    assert result is None


def test_run_exception_handling(tmp_path):
    # Patch evaluator to raise inside run
    class BadEvaluator(PortfolioCrossWindowEvaluator):
        def run(self, strategy_dir):
            raise RuntimeError("fail!")

    evaluator = BadEvaluator(
        logger=MockLoggable(), window_json_filename="window_result.json"
    )
    with pytest.raises(RuntimeError):
        evaluator.run(tmp_path)
