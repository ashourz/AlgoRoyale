import json

import pytest

from algo_royale.backtester.evaluator.portfolio.portfolio_cross_strategy_summary import (
    PortfolioCrossStrategySummary,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def summary():
    return PortfolioCrossStrategySummary(logger=MockLoggable())


def create_strategy_dir(tmp_path, eval_data, strategy_name="strat1"):
    strategy_dir = tmp_path / strategy_name
    strategy_dir.mkdir()
    with open(strategy_dir / "evaluation_result.json", "w") as f:
        json.dump(eval_data, f)
    return strategy_dir


def test_run_valid(tmp_path, summary):
    # Create two strategy dirs with evaluation_result.json
    eval1 = {
        "viability_score": 0.9,
        "param_consistency": 0.8,
        "summary": {"foo": 1},
        "n_windows": 2,
        "metric_type": "both",
        "is_viable": True,
        "most_common_best_params": {"a": 1},
        "window_params": [],
        "strategy": "strat1",
    }
    eval2 = {
        "viability_score": 0.7,
        "param_consistency": 0.9,
        "summary": {"foo": 2},
        "n_windows": 3,
        "metric_type": "both",
        "is_viable": False,
        "most_common_best_params": {"b": 2},
        "window_params": [],
        "strategy": "strat2",
    }
    create_strategy_dir(tmp_path, eval1, "strat1")
    create_strategy_dir(tmp_path, eval2, "strat2")
    result = summary.run(tmp_path)
    assert result is not None
    assert result["viability_score"] == 0.9
    assert result["strategy"] == "strat1"
    # Check output file
    out_path = tmp_path / "summary_result.json"
    assert out_path.exists()
    with open(out_path) as f:
        out_json = json.load(f)
    assert out_json["viability_score"] == 0.9


def test_run_no_evaluation_files(tmp_path, summary):
    # No strategy dirs with evaluation_result.json
    (tmp_path / "strat1").mkdir()
    result = summary.run(tmp_path)
    assert result is None


def test_run_missing_file(tmp_path, summary):
    # Strategy dir exists but no evaluation_result.json
    strat_dir = tmp_path / "strat1"
    strat_dir.mkdir()
    result = summary.run(tmp_path)
    assert result is None


def test_run_invalid_json(tmp_path, summary):
    strat_dir = tmp_path / "strat1"
    strat_dir.mkdir()
    with open(strat_dir / "evaluation_result.json", "w") as f:
        f.write("not a json")
    # Should skip invalid file and return None
    result = summary.run(tmp_path)
    assert result is None


def test_run_not_a_dir(tmp_path, summary):
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("test")
    result = summary.run(file_path)
    assert result is None


def test_run_exception_handling(tmp_path):
    class BadSummary(PortfolioCrossStrategySummary):
        def run(self, symbol_dir):
            raise RuntimeError("fail!")

    summary = BadSummary(logger=MockLoggable())
    with pytest.raises(RuntimeError):
        summary.run(tmp_path)
