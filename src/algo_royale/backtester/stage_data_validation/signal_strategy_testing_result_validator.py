def signal_strategy_testing_validator(d) -> bool:
    """Validate the structure of a signal strategy testing dictionary (the 'test' section)."""
    if not isinstance(d, dict):
        return False
    if "metrics" not in d or not isinstance(d["metrics"], dict):
        return False
    metrics = d["metrics"]
    for k in ["total_return", "sharpe_ratio", "win_rate", "max_drawdown"]:
        if k not in metrics or not isinstance(metrics[k], float):
            return False
    return True


def window_section_validator(win) -> bool:
    """Validate the window section of the testing result."""
    if not isinstance(win, dict):
        return False
    if "start_date" not in win or "end_date" not in win:
        return False
    if not isinstance(win["start_date"], str) or not isinstance(win["end_date"], str):
        return False
    return True


def signal_strategy_testing_result_validator(d) -> bool:
    """
    Validate the structure of a signal strategy testing result dictionary,
    as found in optimization_result.json (for the 'test' key only).
    """
    if not isinstance(d, dict):
        return False
    for window_key, window_val in d.items():
        if not isinstance(window_val, dict):
            return False
        # Must have "test" and "window" keys
        if "test" not in window_val or "window" not in window_val:
            return False
        # Validate "test" section
        if not signal_strategy_testing_validator(window_val["test"]):
            return False
        # Validate "window" section
        if not window_section_validator(window_val["window"]):
            return False
    return True
