from algo_royale.logging.loggable import Loggable
def validate_portfolio_optimization_json_output(output: dict, logger: Loggable) -> bool:
    """
    Validate the structure of a portfolio optimization output JSON.
    """
    if not isinstance(output, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {output}")
        return False
    for window_id, window_data in output.items():
        if not isinstance(window_id, str) or not isinstance(window_data, dict):
            logger.warning(
                f"Validation failed: Window id not str or window data not dict. Id: {window_id}, Data: {window_data}"
            )
            return False
        # Check for required keys
        if "optimization" not in window_data or "window" not in window_data:
            logger.warning(
                f"Validation failed: 'optimization' or 'window' missing. Id: {window_id}, Data: {window_data}"
            )
            return False
        opt = window_data["optimization"]
        win = window_data["window"]
        # Validate optimization section
        if not isinstance(opt, dict):
            logger.warning(
                f"Validation failed: 'optimization' not dict. Id: {window_id}, Value: {opt}"
            )
            return False
        for key in ["strategy", "best_value", "best_params", "meta", "metrics"]:
            if key not in opt:
                logger.warning(
                    f"Validation failed: '{key}' missing in optimization. Id: {window_id}, Data: {opt}"
                )
                return False
        if not isinstance(opt["strategy"], str):
            logger.warning(
                f"Validation failed: 'strategy' not str in optimization. Id: {window_id}, Value: {opt['strategy']}"
            )
            return False
        if not (
            isinstance(opt["best_value"], (float, int))
            or opt["best_value"] in [float("inf"), float("-inf")]
        ):
            logger.warning(
                f"Validation failed: 'best_value' not float/int/inf in optimization. Id: {window_id}, Value: {opt['best_value']}"
            )
            return False
        if not isinstance(opt["best_params"], dict):
            logger.warning(
                f"Validation failed: 'best_params' not dict in optimization. Id: {window_id}, Value: {opt['best_params']}"
            )
            return False
        if not isinstance(opt["meta"], dict):
            logger.warning(
                f"Validation failed: 'meta' not dict in optimization. Id: {window_id}, Value: {opt['meta']}"
            )
            return False
        for meta_key in [
            "run_time_sec",
            "n_trials",
            "symbol",
            "direction",
            "multi_objective",
        ]:
            if meta_key not in opt["meta"]:
                logger.warning(
                    f"Validation failed: '{meta_key}' missing in meta. Id: {window_id}, Value: {opt['meta']}"
                )
                return False
        if not isinstance(opt["metrics"], dict):
            logger.warning(
                f"Validation failed: 'metrics' not dict in optimization. Id: {window_id}, Value: {opt['metrics']}"
            )
            return False
        # Validate window section
        if not isinstance(win, dict):
            logger.warning(
                f"Validation failed: 'window' not dict. Id: {window_id}, Value: {win}"
            )
            return False
        for date_key in ["start_date", "end_date"]:
            if date_key not in win or not isinstance(win[date_key], str):
                logger.warning(
                    f"Validation failed: '{date_key}' missing or not str in window. Id: {window_id}, Value: {win}"
                )
                return False
    return True
