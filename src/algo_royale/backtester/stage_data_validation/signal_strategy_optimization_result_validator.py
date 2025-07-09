from logging import Logger


def signal_strategy_optimization_validator(d, logger: Logger) -> bool:
    """Validate the structure of a signal strategy optimization dictionary."""
    if not isinstance(d, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {d}")
        return False
    required_keys = {"strategy", "best_value", "best_params", "meta", "metrics"}
    if not required_keys.issubset(d):
        logger.warning(f"Validation failed: Missing required keys. Value: {d}")
        return False
    if not isinstance(d["strategy"], str):
        logger.warning(f"Validation failed: 'strategy' not str. Value: {d['strategy']}")
        return False
    if not isinstance(d["best_value"], float):
        logger.warning(
            f"Validation failed: 'best_value' not float. Value: {d['best_value']}"
        )
        return False
    # Validate best_params
    bp = d["best_params"]
    if not isinstance(bp, dict):
        logger.warning(f"Validation failed: 'best_params' not dict. Value: {bp}")
        return False
    for key in ["entry_conditions", "exit_conditions", "trend_conditions"]:
        if key not in bp or not isinstance(bp[key], list):
            logger.warning(
                f"Validation failed: '{key}' missing or not list in best_params. Value: {bp}"
            )
            return False
        for cond in bp[key]:
            if not isinstance(cond, dict):
                logger.warning(
                    f"Validation failed: Condition in '{key}' not dict. Value: {cond}"
                )
                return False
    # Validate meta
    meta = d["meta"]
    if not isinstance(meta, dict):
        logger.warning(f"Validation failed: 'meta' not dict. Value: {meta}")
        return False
    for k in ["run_time_sec", "n_trials", "symbol", "direction"]:
        if k not in meta:
            logger.warning(f"Validation failed: '{k}' missing in meta. Value: {meta}")
            return False
    # Validate metrics
    metrics = d["metrics"]
    if not isinstance(metrics, dict):
        logger.warning(f"Validation failed: 'metrics' not dict. Value: {metrics}")
        return False
    for k in ["total_return", "sharpe_ratio", "win_rate", "max_drawdown"]:
        if k not in metrics or not isinstance(metrics[k], float):
            logger.warning(
                f"Validation failed: '{k}' missing or not float in metrics. Value: {metrics}"
            )
            return False
    return True


def window_section_validator(win, logger: Logger) -> bool:
    """Validate the window section of the optimization result."""
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


def signal_strategy_optimization_result_validator(d: dict, logger: Logger) -> bool:
    """
    Validate the structure of a signal strategy optimization result dictionary,
    as found in optimization_result.json (excluding the 'test' key).
    """
    if not isinstance(d, dict):
        logger
        return False
    for window_key, window_val in d.items():
        if not isinstance(window_val, dict):
            logger.warning(
                f"Validation failed: Window value not dict. Key: {window_key}, Value: {window_val}"
            )
            return False
        # Must have "optimization" and "window" keys
        if "optimization" not in window_val or "window" not in window_val:
            logger.warning(
                f"Validation failed: 'optimization' or 'window' missing in window. Key: {window_key}, Value: {window_val}"
            )
            return False
        # Validate "optimization" section
        if not signal_strategy_optimization_validator(
            window_val["optimization"], logger
        ):
            logger.warning(
                f"Validation failed: 'optimization' section invalid. Key: {window_key}, Value: {window_val['optimization']}"
            )
            return False
        # Validate "window" section
        if not window_section_validator(window_val["window"], logger):
            logger.warning(
                f"Validation failed: 'window' section invalid. Key: {window_key}, Value: {window_val['window']}"
            )
            return False
    return True
