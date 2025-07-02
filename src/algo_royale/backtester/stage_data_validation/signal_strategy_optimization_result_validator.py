def signal_strategy_optimization_validator(d) -> bool:
    """Validate the structure of a signal strategy optimization dictionary."""
    if not isinstance(d, dict):
        return False
    required_keys = {"strategy", "best_value", "best_params", "meta", "metrics"}
    if not required_keys.issubset(d):
        return False
    if not isinstance(d["strategy"], str):
        return False
    if not isinstance(d["best_value"], float):
        return False
    # Validate best_params
    bp = d["best_params"]
    if not isinstance(bp, dict):
        return False
    for key in ["entry_conditions", "exit_conditions", "trend_conditions"]:
        if key not in bp or not isinstance(bp[key], list):
            return False
        for cond in bp[key]:
            if not isinstance(cond, dict):
                return False
    # Validate meta
    meta = d["meta"]
    if not isinstance(meta, dict):
        return False
    for k in ["run_time_sec", "n_trials", "symbol", "direction"]:
        if k not in meta:
            return False
    # Validate metrics
    metrics = d["metrics"]
    if not isinstance(metrics, dict):
        return False
    for k in ["total_return", "sharpe_ratio", "win_rate", "max_drawdown"]:
        if k not in metrics or not isinstance(metrics[k], float):
            return False
    return True


def window_section_validator(win) -> bool:
    """Validate the window section of the optimization result."""
    if not isinstance(win, dict):
        return False
    if "start_date" not in win or "end_date" not in win:
        return False
    if not isinstance(win["start_date"], str) or not isinstance(win["end_date"], str):
        return False
    return True


def signal_strategy_optimization_result_validator(d) -> bool:
    """
    Validate the structure of a signal strategy optimization result dictionary,
    as found in optimization_result.json (excluding the 'test' key).
    """
    if not isinstance(d, dict):
        return False
    for window_key, window_val in d.items():
        if not isinstance(window_val, dict):
            return False
        # Must have "optimization" and "window" keys
        if "optimization" not in window_val or "window" not in window_val:
            return False
        # Validate "optimization" section
        if not signal_strategy_optimization_validator(window_val["optimization"]):
            return False
        # Validate "window" section
        if not window_section_validator(window_val["window"]):
            return False
    return True
