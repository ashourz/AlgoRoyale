import json

import pytest

from algo_royale.backtester.evaluator.symbol.symbol_evaluation_coordinator import (
    SymbolEvaluationCoordinator,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def symbol_eval_dir(tmp_path):
    symbol_dir = tmp_path / "SYM1"
    symbol_dir.mkdir()
    strat1_dir = symbol_dir / "STRAT1"
    strat1_dir.mkdir()
    strat2_dir = symbol_dir / "STRAT2"
    strat2_dir.mkdir()
    return tmp_path, symbol_dir, strat1_dir, strat2_dir


def make_eval_json(strat_dir, filename, content):
    file_path = strat_dir / filename
    with open(file_path, "w") as f:
        json.dump(content, f)
    return file_path


def valid_eval_report(strategy, viability_score=0.8, param_consistency=0.9):
    return {
        "summary": {
            "total_return": {"mean": 0.1, "std": 0.01, "min": 0.09, "max": 0.11},
            "sharpe_ratio": {"mean": 1.0, "std": 0.1, "min": 0.9, "max": 1.1},
            "win_rate": {"mean": 0.8, "std": 0.05, "min": 0.75, "max": 0.85},
            "max_drawdown": {"mean": 0.2, "std": 0.02, "min": 0.18, "max": 0.22},
        },
        "n_windows": 2,
        "metric_type": "OPTIMIZATION",
        "viability_score": viability_score,
        "is_viable": viability_score >= 0.75,
        "most_common_best_params": {
            "entry_conditions": [],
            "exit_conditions": [],
            "filter_conditions": [],
            "trend_conditions": [],
            "stateful_logic": {},
        },
        "param_consistency": param_consistency,
        "window_params": [
            {
                "entry_conditions": [],
                "exit_conditions": [],
                "filter_conditions": [],
                "trend_conditions": [],
                "stateful_logic": {},
            }
        ],
        "strategy": strategy,
    }


def test_run_selects_best_strategy(symbol_eval_dir):
    tmp_path, symbol_dir, strat1_dir, strat2_dir = symbol_eval_dir
    eval_json = "eval.json"
    # strat1 is viable, strat2 is not
    make_eval_json(
        strat1_dir,
        eval_json,
        valid_eval_report("STRAT1", viability_score=0.8, param_consistency=0.9),
    )
    make_eval_json(
        strat2_dir,
        eval_json,
        valid_eval_report("STRAT2", viability_score=0.6, param_consistency=0.5),
    )
    logger = MockLoggable()
    coordinator = SymbolEvaluationCoordinator(
        optimization_root=str(tmp_path),
        evaluation_json_filename=eval_json,
        summary_json_filename="summary.json",
        logger=logger,
        viability_threshold=0.75,
    )
    coordinator.run()
    summary_path = symbol_dir / "summary.json"
    assert summary_path.exists()
    with open(summary_path) as f:
        summary = json.load(f)
    assert summary["strategy"] == "STRAT1"
    assert summary["viability_score"] >= 0.75


def test_run_handles_no_viable_strategy(symbol_eval_dir):
    tmp_path, symbol_dir, strat1_dir, strat2_dir = symbol_eval_dir
    eval_json = "eval.json"
    # Both below threshold
    make_eval_json(
        strat1_dir,
        eval_json,
        valid_eval_report("STRAT1", viability_score=0.6, param_consistency=0.5),
    )
    make_eval_json(
        strat2_dir,
        eval_json,
        valid_eval_report("STRAT2", viability_score=0.7, param_consistency=0.7),
    )
    logger = MockLoggable()
    coordinator = SymbolEvaluationCoordinator(
        optimization_root=str(tmp_path),
        evaluation_json_filename=eval_json,
        summary_json_filename="summary.json",
        logger=logger,
        viability_threshold=0.75,
    )
    coordinator.run()
    summary_path = symbol_dir / "summary.json"
    assert summary_path.exists()
    with open(summary_path) as f:
        summary = json.load(f)
    # Should pick the one with highest viability_score
    assert summary["strategy"] == "STRAT2"
    assert summary["viability_score"] == 0.7


def test_run_handles_invalid_eval_json(symbol_eval_dir):
    tmp_path, symbol_dir, strat1_dir, strat2_dir = symbol_eval_dir
    eval_json = "eval.json"
    # strat1 has invalid json
    (strat1_dir / eval_json).write_text("not a json")
    make_eval_json(
        strat2_dir,
        eval_json,
        valid_eval_report("STRAT2", viability_score=0.8, param_consistency=0.9),
    )
    logger = MockLoggable()
    coordinator = SymbolEvaluationCoordinator(
        optimization_root=str(tmp_path),
        evaluation_json_filename=eval_json,
        summary_json_filename="summary.json",
        logger=logger,
        viability_threshold=0.75,
    )
    coordinator.run()
    summary_path = symbol_dir / "summary.json"
    assert summary_path.exists()
    with open(summary_path) as f:
        summary = json.load(f)
    assert summary["strategy"] == "STRAT2"


def test_run_handles_no_results(symbol_eval_dir):
    tmp_path, symbol_dir, strat1_dir, strat2_dir = symbol_eval_dir
    eval_json = "eval.json"
    # No eval.json files
    logger = MockLoggable()
    coordinator = SymbolEvaluationCoordinator(
        optimization_root=str(tmp_path),
        evaluation_json_filename=eval_json,
        summary_json_filename="summary.json",
        logger=logger,
        viability_threshold=0.75,
    )
    coordinator.run()
    summary_path = symbol_dir / "summary.json"
    assert not summary_path.exists()


def test_run_exception_handling(symbol_eval_dir):
    tmp_path, symbol_dir, strat1_dir, strat2_dir = symbol_eval_dir
    eval_json = "eval.json"
    make_eval_json(
        strat1_dir,
        eval_json,
        valid_eval_report("STRAT1", viability_score=0.8, param_consistency=0.9),
    )
    make_eval_json(
        strat2_dir,
        eval_json,
        valid_eval_report("STRAT2", viability_score=0.8, param_consistency=0.9),
    )
    logger = MockLoggable()

    # Patch the coordinator to raise an exception
    class BrokenCoordinator(SymbolEvaluationCoordinator):
        def run(self):
            raise RuntimeError("Simulated error")

    broken = BrokenCoordinator(
        optimization_root=str(tmp_path),
        evaluation_json_filename=eval_json,
        summary_json_filename="summary.json",
        logger=logger,
        viability_threshold=0.75,
    )
    with pytest.raises(RuntimeError):
        broken.run()
