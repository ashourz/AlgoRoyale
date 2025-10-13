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
    as found in optimization_result.json (single test result).
    Expected keys: 'test', 'window', 'optimization'
    """
    if not isinstance(d, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {d}")
        return False

    required_keys = ["test", "window", "optimization"]
    for key in required_keys:
        if key not in d:
            logger.warning(f"Validation failed: Missing key '{key}'. Value: {d}")
            return False

    # Validate 'test' section
    if not signal_strategy_testing_validator(d["test"], logger):
        logger.warning(f"Validation failed: 'test' section invalid. Value: {d['test']}")
        return False

    # Validate 'window' section
    if not window_section_validator(d["window"], logger):
        logger.warning(
            f"Validation failed: 'window' section invalid. Value: {d['window']}"
        )
        return False

    # Validate 'optimization' section
    optimization = d["optimization"]
    if not isinstance(optimization, dict):
        logger.warning(
            f"Validation failed: 'optimization' not dict. Value: {optimization}"
        )
        return False
    for opt_key in ["strategy", "best_value", "best_params", "meta", "metrics"]:
        if opt_key not in optimization:
            logger.warning(
                f"Validation failed: '{opt_key}' missing in optimization. Value: {optimization}"
            )
            return False

    # Optionally, validate optimization['metrics'] structure
    metrics = optimization["metrics"]
    for k in ["total_return", "sharpe_ratio", "win_rate", "max_drawdown"]:
        if k not in metrics:
            logger.warning(
                f"Validation failed: '{k}' missing in optimization metrics. Value: {metrics}"
            )
            return False

    return True
