from algo_royale.logging.loggable import Loggable


def validate_portfolio_testing_json_output(output: dict, logger: Loggable) -> bool:
    """
    Validate the structure of a portfolio testing output JSON.
    Expected: {
        window_id: {
            "test": {
                "strategy": str,
                "params": dict,
                "meta": {
                    "symbols": list,
                    "window_id": str,
                    "transactions": list
                },
                "metrics": dict,
                "window": {
                    "start_date": str,
                    "end_date": str,
                    "window_id": str
                }
            }
        }
    }
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
        # Check for required 'test' key
        if "test" not in window_data:
            logger.warning(
                f"Validation failed: 'test' missing. Id: {window_id}, Data: {window_data}"
            )
            return False
        test = window_data["test"]
        if not isinstance(test, dict):
            logger.warning(
                f"Validation failed: 'test' not dict. Id: {window_id}, Value: {test}"
            )
            return False
        # Check required keys in 'test'
        required_keys = ["strategy", "params", "meta", "metrics", "window"]
        for key in required_keys:
            if key not in test:
                logger.warning(
                    f"Validation failed: '{key}' missing in test. Id: {window_id}, Data: {test}"
                )
                return False
        if not isinstance(test["strategy"], str):
            logger.warning(
                f"Validation failed: 'strategy' not str in test. Id: {window_id}, Value: {test['strategy']}"
            )
            return False
        if not isinstance(test["params"], dict):
            logger.warning(
                f"Validation failed: 'params' not dict in test. Id: {window_id}, Value: {test['params']}"
            )
            return False
        # Validate meta
        meta = test["meta"]
        if not isinstance(meta, dict):
            logger.warning(
                f"Validation failed: 'meta' not dict in test. Id: {window_id}, Value: {meta}"
            )
            return False
        if "symbols" not in meta or not isinstance(meta["symbols"], list):
            logger.warning(
                f"Validation failed: 'symbols' missing or not list in meta. Id: {window_id}, Value: {meta}"
            )
            return False
        if "window_id" not in meta or not isinstance(meta["window_id"], str):
            logger.warning(
                f"Validation failed: 'window_id' missing or not str in meta. Id: {window_id}, Value: {meta}"
            )
            return False
        if "transactions" not in meta or not isinstance(meta["transactions"], list):
            logger.warning(
                f"Validation failed: 'transactions' missing or not list in meta. Id: {window_id}, Value: {meta}"
            )
            return False
        # Validate metrics
        if not isinstance(test["metrics"], dict):
            logger.warning(
                f"Validation failed: 'metrics' not dict in test. Id: {window_id}, Value: {test['metrics']}"
            )
            return False
        # Validate window section
        win = test["window"]
        if not isinstance(win, dict):
            logger.warning(
                f"Validation failed: 'window' not dict in test. Id: {window_id}, Value: {win}"
            )
            return False
        for date_key in ["start_date", "end_date", "window_id"]:
            if date_key not in win or not isinstance(win[date_key], str):
                logger.warning(
                    f"Validation failed: '{date_key}' missing or not str in window. Id: {window_id}, Value: {win}"
                )
                return False


def validate_portfolio_optimization_testing_stage_coordinator_input(
    input_data: dict, logger: Loggable
) -> bool:
    """Validate the input structure for portfolio optimization results (single strategy, single symbol)."""
    if not isinstance(input_data, dict):
        logger.warning(
            f"Validation failed: input_data is not a dictionary. Value: {input_data}"
        )
        return False
    for window_id, window_data in input_data.items():
        if not isinstance(window_id, str):
            logger.warning(
                f"Validation failed: window_id is not a string. Key: {window_id}"
            )
            return False
        if not isinstance(window_data, dict):
            logger.warning(
                f"Validation failed: window_data is not a dict. Value: {window_data}"
            )
            return False
        # Must have 'optimization' and 'window'
        if "optimization" not in window_data or "window" not in window_data:
            logger.warning(
                f"Validation failed: 'optimization' or 'window' missing in window_data. Window ID: {window_id}, Value: {window_data}"
            )
            return False
        optimization = window_data["optimization"]
        win = window_data["window"]
        # Validate optimization section
        if not isinstance(optimization, dict):
            logger.warning(
                f"Validation failed: 'optimization' is not a dict. Window ID: {window_id}, Value: {optimization}"
            )
            return False
        for key in [
            "strategy",
            "best_value",
            "best_params",
            "meta",
            "metrics",
            "window",
        ]:
            if key not in optimization:
                logger.warning(
                    f"Validation failed: '{key}' missing in optimization. Window ID: {window_id}, Value: {optimization}"
                )
                return False
        if not isinstance(optimization["strategy"], str):
            logger.warning(
                f"Validation failed: 'strategy' not str in optimization. Window ID: {window_id}"
            )
            return False
        if not isinstance(optimization["best_params"], dict):
            logger.warning(
                f"Validation failed: 'best_params' not dict in optimization. Window ID: {window_id}"
            )
            return False
        if not isinstance(optimization["meta"], dict):
            logger.warning(
                f"Validation failed: 'meta' not dict in optimization. Window ID: {window_id}"
            )
            return False
        if not isinstance(optimization["metrics"], dict):
            logger.warning(
                f"Validation failed: 'metrics' not dict in optimization. Window ID: {window_id}"
            )
            return False
        if not isinstance(optimization["window"], dict):
            logger.warning(
                f"Validation failed: 'window' not dict in optimization. Window ID: {window_id}"
            )
            return False
        # Validate window section
        if not isinstance(win, dict):
            logger.warning(
                f"Validation failed: 'window' not dict at top level. Window ID: {window_id}"
            )
            return False
        for date_key in ["start_date", "end_date", "window_id"]:
            if date_key not in win or not isinstance(win[date_key], str):
                logger.warning(
                    f"Validation failed: '{date_key}' missing or not str in window. Window ID: {window_id}, Value: {win}"
                )
                return False
    return True
