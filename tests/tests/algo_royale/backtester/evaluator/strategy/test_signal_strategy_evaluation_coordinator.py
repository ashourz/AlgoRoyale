import json

import pytest

from algo_royale.backtester.evaluator.strategy.signal_strategy_evaluation_coordinator import (
    SignalStrategyEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.strategy.strategy_evaluation_type import (
    StrategyEvaluationType,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def temp_optimization_dir(tmp_path):
    symbol_dir = tmp_path / "SYM1"
    symbol_dir.mkdir()
    strat_dir = symbol_dir / "STRAT1"
    strat_dir.mkdir()
    return tmp_path, symbol_dir, strat_dir


def make_opt_json(strat_dir, filename, content):
    file_path = strat_dir / filename
    with open(file_path, "w") as f:
        json.dump(content, f)
    return file_path


def test_run_success(temp_optimization_dir):
    tmp_path, symbol_dir, strat_dir = temp_optimization_dir
    # Debug: Ensure the file exists and print directory contents
    opt_path = strat_dir / "opt.json"
    # The file is created below, so this assertion will be after make_opt_json
    # Mock optimization result that will produce a valid evaluation report
    # best_params must have at least one expected key (e.g., entry_conditions as a list of dicts)
    best_params = {
        "entry_conditions": [{"cond": 1}],
        "exit_conditions": [{"cond": 2}],
        "filter_conditions": [{"cond": 3}],
        "trend_conditions": [{"cond": 4}],
        "stateful_logic": {},
    }
    opt_content = {
        "window1": {
            "window": {"start_date": "2020-01-01", "end_date": "2020-06-30"},
            "optimization": {
                "strategy": "TestStrategy",
                "best_value": 1.23,
                "best_params": best_params,
                "meta": {
                    "run_time_sec": 1.0,
                    "n_trials": 10,
                    "symbol": "SYM1",
                    "direction": "long",
                },
                "metrics": {
                    "total_return": 0.1,
                    "sharpe_ratio": 1.0,
                    "win_rate": 0.8,
                    "max_drawdown": 0.2,
                },
            },
            "test": {},
        },
        "window2": {
            "window": {"start_date": "2020-07-01", "end_date": "2020-12-31"},
            "optimization": {
                "strategy": "TestStrategy",
                "best_value": 2.34,
                "best_params": best_params,
                "meta": {
                    "run_time_sec": 2.0,
                    "n_trials": 20,
                    "symbol": "SYM1",
                    "direction": "long",
                },
                "metrics": {
                    "total_return": 0.2,
                    "sharpe_ratio": 1.2,
                    "win_rate": 0.9,
                    "max_drawdown": 0.1,
                },
            },
            "test": {},
        },
    }
    make_opt_json(strat_dir, "opt.json", opt_content)
    # Debug: Ensure the file exists and print directory contents
    opt_path = strat_dir / "opt.json"
    assert opt_path.exists(), f"opt.json not found at {opt_path}"
    print(f"Files in {strat_dir}: {[p.name for p in strat_dir.iterdir()]}")
    logger = MockLoggable()
    coordinator = SignalStrategyEvaluationCoordinator(
        logger=logger,
        optimization_root=str(tmp_path),
        evaluation_type=StrategyEvaluationType.OPTIMIZATION,
        optimization_json_filename="opt.json",
        evaluation_json_filename="eval.json",
    )
    coordinator.run()
    # Print logger messages for debugging
    if hasattr(logger, "messages"):
        print("Logger messages:")
        for msg in logger.messages:
            print(msg)
    eval_path = strat_dir / "eval.json"
    assert eval_path.exists()
    with open(eval_path) as f:
        report = json.load(f)
    assert report["viability_score"] >= 0
    assert report["is_viable"] in [True, False]


def test_run_handles_missing_dir(tmp_path):
    logger = MockLoggable()
    coordinator = SignalStrategyEvaluationCoordinator(
        logger=logger,
        optimization_root=str(tmp_path / "doesnotexist"),
        evaluation_type=StrategyEvaluationType.OPTIMIZATION,
        optimization_json_filename="opt.json",
        evaluation_json_filename="eval.json",
    )
    # Should not raise, should create dir
    coordinator.run()
    assert (tmp_path / "doesnotexist").exists()


def test_run_handles_invalid_json(temp_optimization_dir):
    tmp_path, symbol_dir, strat_dir = temp_optimization_dir
    # Write invalid JSON
    file_path = strat_dir / "opt.json"
    file_path.write_text("not a json")
    logger = MockLoggable()
    coordinator = SignalStrategyEvaluationCoordinator(
        logger=logger,
        optimization_root=str(tmp_path),
        evaluation_type=StrategyEvaluationType.OPTIMIZATION,
        optimization_json_filename="opt.json",
        evaluation_json_filename="eval.json",
    )
    # Should log error but not raise
    coordinator.run()
    # No eval.json should be created
    assert not (strat_dir / "eval.json").exists()


def test_write_aggregated_evaluation_report(temp_optimization_dir):
    _, _, strat_dir = temp_optimization_dir
    logger = MockLoggable()
    coordinator = SignalStrategyEvaluationCoordinator(
        logger=logger,
        optimization_root=str(strat_dir),
        evaluation_type=StrategyEvaluationType.OPTIMIZATION,
        optimization_json_filename="opt.json",
        evaluation_json_filename="eval.json",
    )
    report = {"foo": "bar"}
    coordinator.write_aggregated_evaluation_report(strat_dir, report)
    eval_path = strat_dir / "eval.json"
    assert eval_path.exists()
    with open(eval_path) as f:
        data = json.load(f)
    assert data == report
