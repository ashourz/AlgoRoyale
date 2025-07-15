from algo_royale.logging.loggable import Loggable


def signal_strategy_testing_validator(d, logger: Loggable) -> bool:
    """Validate the structure of a signal strategy testing dictionary (the 'test' section)."""
    if not isinstance(d, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {d}")
        return False
    if "metrics" not in d or not isinstance(d["metrics"], dict):
        logger.warning(f"Validation failed: 'metrics' missing or not dict. Value: {d}")
        return False
    metrics = d["metrics"]
    for k in ["total_return", "sharpe_ratio", "win_rate", "max_drawdown"]:
        if k not in metrics:
            logger.warning(
                f"Validation failed: '{k}' missing in metrics. Value: {metrics}"
            )
            return False
        v = metrics[k]
        if v is None:
            logger.warning(
                f"Validation warning: '{k}' is None in metrics. Value: {metrics}"
            )
            continue  # Warn but do not fail
        if not isinstance(v, (float, int)):
            logger.warning(
                f"Validation failed: '{k}' not float or int in metrics. Value: {metrics}"
            )
            return False
    return True


def window_section_validator(win, logger: Loggable) -> bool:
    """Validate the window section of the testing result."""
    if not isinstance(win, dict):
        logger.warning(f"Validation failed: Window section not dict. Value: {win}")
        return False
    if "start_date" not in win or "end_date" not in win:
        logger.warning(
            f"Validation failed: 'start_date' or 'end_date' missing in window. Value: {win}"
        )
        return False
    if not isinstance(win["start_date"], str) or not isinstance(win["end_date"], str):
        logger.warning(
            f"Validation failed: 'start_date' or 'end_date' not str. Value: {win}"
        )
        return False
    return True


def signal_strategy_testing_result_validator(d, logger: Loggable) -> bool:
    """
    Validate the structure of a signal strategy testing result dictionary,
    as found in optimization_result.json (for the 'test' key only).
    """
    if not isinstance(d, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {d}")
        return False

    if not d:  # Check for empty dict
        logger.warning("Validation failed: Testing result dict is empty.")
        return False

    for window_key, window_val in d.items():
        if not isinstance(window_val, dict):
            logger.warning(
                f"Validation failed: Window value not dict. Key: {window_key}, Value: {window_val}"
            )
            return False
        # Must have "test" and "window" keys
        if "test" not in window_val or "window" not in window_val:
            logger.warning(
                f"Validation failed: 'test' or 'window' missing in window value. Key: {window_key}, Value: {window_val}"
            )
            return False
        # Validate "test" section
        if not signal_strategy_testing_validator(window_val["test"], logger):
            logger.warning(
                f"Validation failed: 'test' section invalid. Key: {window_key}, Value: {window_val['test']}"
            )
            return False
        # Validate "window" section
        if not window_section_validator(window_val["window"], logger):
            logger.warning(
                f"Validation failed: 'window' section invalid. Key: {window_key}, Value: {window_val['window']}"
            )
            return False
    return True
