from logging import Logger


def summary_metric_validator(metric, logger: Logger) -> bool:
    """Validate a summary metric dict with mean, std, min, max (all floats)."""
    if not isinstance(metric, dict):
        logger.warning(f"Validation failed: Metric not dict. Value: {metric}")
        return False
    for k in ["mean", "std", "min", "max"]:
        if k not in metric or not isinstance(metric[k], float):
            logger.warning(
                f"Validation failed: '{k}' missing or not float in metric. Value: {metric}"
            )
            return False
    return True


def most_common_best_params_validator(params, logger: Logger) -> bool:
    """Validate the most_common_best_params or window_params entry."""
    if not isinstance(params, dict):
        logger.warning(f"Validation failed: Params not dict. Value: {params}")
        return False
    for key in ["entry_conditions", "exit_conditions", "trend_conditions"]:
        if key not in params or not isinstance(params[key], list):
            logger.warning(
                f"Validation failed: '{key}' missing or not list in params. Value: {params}"
            )
            return False
        for cond in params[key]:
            if not isinstance(cond, dict):
                logger.warning(
                    f"Validation failed: Condition in '{key}' not dict. Value: {cond}"
                )
                return False
    return True


def window_params_validator(window_params, logger: Logger) -> bool:
    """Validate the window_params list."""
    if not isinstance(window_params, list):
        logger.warning(
            f"Validation failed: window_params not list. Value: {window_params}"
        )
        return False
    for param in window_params:
        if not most_common_best_params_validator(param, logger):
            logger.warning(
                f"Validation failed: window_params entry invalid. Value: {param}"
            )
            return False
    return True


def signal_evaluation_result_validator(d, logger: Logger) -> bool:
    """Validate the structure of evaluation_result.json."""
    if not isinstance(d, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {d}")
        return False
    # Validate summary
    if "summary" not in d or not isinstance(d["summary"], dict):
        logger.warning(f"Validation failed: 'summary' missing or not dict. Value: {d}")
        return False
    for metric in ["total_return", "sharpe_ratio", "win_rate", "max_drawdown"]:
        if metric not in d["summary"] or not summary_metric_validator(
            d["summary"][metric], logger
        ):
            logger.warning(
                f"Validation failed: '{metric}' summary metric invalid. Value: {d['summary'].get(metric)}"
            )
            return False
    # Validate scalar fields
    if "n_windows" not in d or not isinstance(d["n_windows"], int):
        logger.warning(
            f"Validation failed: 'n_windows' missing or not int. Value: {d.get('n_windows')}"
        )
        return False
    if "metric_type" not in d or not isinstance(d["metric_type"], str):
        logger.warning(
            f"Validation failed: 'metric_type' missing or not str. Value: {d.get('metric_type')}"
        )
        return False
    if "viability_score" not in d or not isinstance(d["viability_score"], float):
        logger.warning(
            f"Validation failed: 'viability_score' missing or not float. Value: {d.get('viability_score')}"
        )
        return False
    if "is_viable" not in d or not isinstance(d["is_viable"], bool):
        logger.warning(
            f"Validation failed: 'is_viable' missing or not bool. Value: {d.get('is_viable')}"
        )
        return False
    # Validate most_common_best_params
    if "most_common_best_params" not in d or not most_common_best_params_validator(
        d["most_common_best_params"], logger
    ):
        logger.warning(
            f"Validation failed: 'most_common_best_params' invalid. Value: {d.get('most_common_best_params')}"
        )
        return False
    # Validate param_consistency
    if "param_consistency" not in d or not isinstance(d["param_consistency"], float):
        logger.warning(
            f"Validation failed: 'param_consistency' missing or not float. Value: {d.get('param_consistency')}"
        )
        return False
    # Validate window_params
    if "window_params" not in d or not window_params_validator(
        d["window_params"], logger
    ):
        logger.warning(
            f"Validation failed: 'window_params' invalid. Value: {d.get('window_params')}"
        )
        return False
    return True
