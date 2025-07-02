def summary_metric_validator(metric) -> bool:
    """Validate a summary metric dict with mean, std, min, max (all floats)."""
    if not isinstance(metric, dict):
        return False
    for k in ["mean", "std", "min", "max"]:
        if k not in metric or not isinstance(metric[k], float):
            return False
    return True


def most_common_best_params_validator(params) -> bool:
    """Validate the most_common_best_params or window_params entry."""
    if not isinstance(params, dict):
        return False
    for key in ["entry_conditions", "exit_conditions", "trend_conditions"]:
        if key not in params or not isinstance(params[key], list):
            return False
        for cond in params[key]:
            if not isinstance(cond, dict):
                return False
    return True


def window_params_validator(window_params) -> bool:
    """Validate the window_params list."""
    if not isinstance(window_params, list):
        return False
    for param in window_params:
        if not most_common_best_params_validator(param):
            return False
    return True


def signal_summary_validator(d) -> bool:
    """Validate the structure of summary_result.json."""
    if not isinstance(d, dict):
        return False
    # Validate summary
    if "summary" not in d or not isinstance(d["summary"], dict):
        return False
    for metric in ["total_return", "sharpe_ratio", "win_rate", "max_drawdown"]:
        if metric not in d["summary"] or not summary_metric_validator(
            d["summary"][metric]
        ):
            return False
    # Validate scalar fields
    if "n_windows" not in d or not isinstance(d["n_windows"], int):
        return False
    if "metric_type" not in d or not isinstance(d["metric_type"], str):
        return False
    if "viability_score" not in d or not isinstance(d["viability_score"], float):
        return False
    if "is_viable" not in d or not isinstance(d["is_viable"], bool):
        return False
    # Validate most_common_best_params
    if "most_common_best_params" not in d or not most_common_best_params_validator(
        d["most_common_best_params"]
    ):
        return False
    # Validate param_consistency
    if "param_consistency" not in d or not isinstance(d["param_consistency"], float):
        return False
    # Validate window_params
    if "window_params" not in d or not window_params_validator(d["window_params"]):
        return False
    # Validate strategy
    if "strategy" not in d or not isinstance(d["strategy"], str):
        return False
    return True
