import json
from unittest.mock import MagicMock

import pytest

from algo_royale.backtester.evaluator.portfolio.portfolio_evaluation_coordinator import (
    PortfolioEvaluationCoordinator,
)


def make_eval_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(content, f)


@pytest.fixture
def tmp_evaluation_dir(tmp_path):
    # Structure: root/symbol/strategy/eval.json
    root = tmp_path / "eval_root"
    symbol_dir = root / "AAPL"
    strat1_dir = symbol_dir / "Strat1"
    strat2_dir = symbol_dir / "Strat2"
    eval1 = {
        "viability_score": 0.8,
        "param_consistency": 0.9,
        "allocation_params": {"x": 1},
    }
    eval2 = {
        "viability_score": 0.7,
        "param_consistency": 0.8,
        "allocation_params": {"x": 2},
    }
    make_eval_file(strat1_dir / "eval.json", eval1)
    make_eval_file(strat2_dir / "eval.json", eval2)
    return root


def test_portfolio_evaluation_coordinator_selects_best(tmp_evaluation_dir):
    logger = MagicMock()
    coordinator = PortfolioEvaluationCoordinator(
        logger=logger,
        optimization_root=tmp_evaluation_dir,
        strategy_window_evaluation_json_filename="eval.json",
        strategy_summary_json_filename="summary.json",
        global_summary_json_filename="global.json",
        viability_threshold=0.75,
    )
    coordinator.run()
    # Check that summary and global summary files exist and are correct
    summary_path = tmp_evaluation_dir / "AAPL" / "summary.json"
    global_path = tmp_evaluation_dir / "global.json"
    assert summary_path.exists()
    assert global_path.exists()
    with open(summary_path) as f:
        summary = json.load(f)
    with open(global_path) as f:
        global_summary = json.load(f)
    # Should select Strat1 as best (viability_score=0.8 > threshold)
    assert summary["recommended_strategy"] == "Strat1"
    assert global_summary["AAPL"]["recommended_strategy"] == "Strat1"
    assert summary["viability_score"] == 0.8
    assert summary["param_consistency"] == 0.9
    assert summary["allocation_params"] == {"x": 1}


def test_portfolio_evaluation_coordinator_fallback(tmp_path):
    # Only one strategy, below threshold
    root = tmp_path / "eval_root"
    symbol_dir = root / "AAPL"
    strat_dir = symbol_dir / "Strat1"
    eval1 = {
        "viability_score": 0.5,
        "param_consistency": 0.7,
        "allocation_params": {"x": 3},
    }

    def make_eval_file(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(content, f)

    make_eval_file(strat_dir / "eval.json", eval1)
    logger = MagicMock()
    coordinator = PortfolioEvaluationCoordinator(
        logger=logger,
        optimization_root=root,
        strategy_window_evaluation_json_filename="eval.json",
        strategy_summary_json_filename="summary.json",
        global_summary_json_filename="global.json",
        viability_threshold=0.75,
    )
    coordinator.run()
    summary_path = root / "AAPL" / "summary.json"
    with open(summary_path) as f:
        summary = json.load(f)
    # Should fallback to best available
    assert summary["recommended_strategy"] == "Strat1"
    assert summary["viability_score"] == 0.5
    assert summary["param_consistency"] == 0.7
    assert summary["allocation_params"] == {"x": 3}
