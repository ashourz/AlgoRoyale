from typing import Any, Dict


def validate_portfolio_evaluation_input_json(output: Dict[str, Any]) -> bool:
    """
    Validate that the input JSON for PortfolioEvaluationCoordinator contains both
    valid optimization and testing structures for each window.
    """
    if not isinstance(output, dict):
        return False
    for window_id, window_data in output.items():
        if not isinstance(window_id, str) or not isinstance(window_data, dict):
            return False
        # Must have a window section
        if "window" not in window_data or not isinstance(window_data["window"], dict):
            return False
        for date_key in ["start_date", "end_date"]:
            if date_key not in window_data["window"] or not isinstance(
                window_data["window"][date_key], str
            ):
                return False
        # Must have at least one of optimization or test
        has_optimization = "optimization" in window_data and isinstance(
            window_data["optimization"], dict
        )
        has_test = "test" in window_data and isinstance(window_data["test"], dict)
        if not (has_optimization and has_test):
            return False
        # Validate optimization section
        opt = window_data["optimization"]
        for key in ["strategy", "best_value", "best_params", "meta", "metrics"]:
            if key not in opt:
                return False
        if not isinstance(opt["strategy"], str):
            return False
        if not (
            isinstance(opt["best_value"], (float, int))
            or opt["best_value"] in [float("inf"), float("-inf")]
        ):
            return False
        if not isinstance(opt["best_params"], dict):
            return False
        if not isinstance(opt["meta"], dict):
            return False
        for meta_key in [
            "run_time_sec",
            "n_trials",
            "symbol",
            "direction",
            "multi_objective",
        ]:
            if meta_key not in opt["meta"]:
                return False
        if not isinstance(opt["metrics"], dict) or "metrics" not in opt["metrics"]:
            return False
        # Validate test section
        test = window_data["test"]
        if "metrics" not in test or "transactions" not in test:
            return False
        if not isinstance(test["metrics"], dict):
            return False
        if not isinstance(test["transactions"], list):
            return False
    return True


def validate_portfolio_evaluation_output_json(output: dict) -> bool:
    """
    Validate the structure of the output JSON produced by PortfolioEvaluationCoordinator.
    Expected: {symbol: { ...summary fields... }}
    """
    if not isinstance(output, dict):
        return False
    for symbol, summary in output.items():
        if not isinstance(symbol, str) or not isinstance(summary, dict):
            return False
        required_keys = [
            "symbol",
            "recommended_strategy",
            "viability_score",
            "param_consistency",
            "metrics",
            "allocation_params",
            "rationale",
        ]
        for key in required_keys:
            if key not in summary:
                return False
        if not isinstance(summary["symbol"], str):
            return False
        if not isinstance(summary["recommended_strategy"], str):
            return False
        # viability_score and param_consistency can be float or None
        if summary["viability_score"] is not None and not isinstance(
            summary["viability_score"], (float, int)
        ):
            return False
        if summary["param_consistency"] is not None and not isinstance(
            summary["param_consistency"], (float, int)
        ):
            return False
        if not isinstance(summary["metrics"], dict):
            return False
        if not isinstance(summary["allocation_params"], dict):
            return False
        if not isinstance(summary["rationale"], str):
            return False
    return True
