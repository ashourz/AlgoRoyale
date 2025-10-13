import json

import pytest

from algo_royale.backtester.evaluator.strategy.strategy_evaluation_type import (
    StrategyEvaluationType,
)
from algo_royale.backtester.evaluator.strategy.strategy_evaluator import (
    StrategyEvaluator,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def valid_results(tmp_path):
    file_path = tmp_path / "results.json"
    content = {
        "window1": {
            "window": {"start_date": "2020-01-01", "end_date": "2020-06-30"},
            "optimization": {
                "metrics": {
                    "total_return": 0.1,
                    "sharpe_ratio": 1.0,
                    "win_rate": 0.8,
                    "max_drawdown": 0.2,
                }
            },
            "test": {
                "metrics": {
                    "total_return": 0.2,
                    "sharpe_ratio": 1.2,
                    "win_rate": 0.9,
                    "max_drawdown": 0.1,
                }
            },
        }
    }
    with open(file_path, "w") as f:
        json.dump(content, f)
    return file_path


def test_load_data_and_metrics(valid_results):
    logger = MockLoggable()
    evaluator = StrategyEvaluator(
        logger=logger, metric_type=StrategyEvaluationType.BOTH
    )
    evaluator.load_data(valid_results)
    assert evaluator.results is not None
    assert evaluator.metrics is not None
    assert any(m["type"] == "optimization" for m in evaluator.metrics)
    assert any(m["type"] == "test" for m in evaluator.metrics)


def test_load_data_invalid_json(tmp_path):
    file_path = tmp_path / "bad.json"
    file_path.write_text("not a json")
    logger = MockLoggable()
    evaluator = StrategyEvaluator(
        logger=logger, metric_type=StrategyEvaluationType.BOTH
    )
    with pytest.raises(json.JSONDecodeError):
        evaluator.load_data(file_path)


def test_load_data_invalid_results(tmp_path):
    file_path = tmp_path / "invalid.json"
    # Write valid JSON but not valid results
    with open(file_path, "w") as f:
        json.dump({"foo": "bar"}, f)
    logger = MockLoggable()
    evaluator = StrategyEvaluator(
        logger=logger, metric_type=StrategyEvaluationType.BOTH
    )
    with pytest.raises(ValueError):
        evaluator.load_data(file_path)


def test_summary_and_viability_score(valid_results):
    logger = MockLoggable()
    evaluator = StrategyEvaluator(
        logger=logger, metric_type=StrategyEvaluationType.BOTH
    )
    evaluator.load_data(valid_results)
    summary = evaluator.summary()
    assert isinstance(summary, dict)
    score = evaluator.viability_score()
    assert 0 <= score <= 1
    is_viable = evaluator.is_viable()
    assert isinstance(is_viable, bool)


def test_summary_empty():
    logger = MockLoggable()
    evaluator = StrategyEvaluator(
        logger=logger, metric_type=StrategyEvaluationType.BOTH
    )
    evaluator.metrics = []
    assert evaluator.summary() == {}
    assert evaluator.viability_score() == 0
    assert evaluator.is_viable() is False
