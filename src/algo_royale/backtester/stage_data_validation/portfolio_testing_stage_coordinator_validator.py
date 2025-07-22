from algo_royale.logging.loggable import Loggable


def validate_portfolio_testing_json_output(output: dict, logger: Loggable) -> bool:
    """
    Validate the structure of a portfolio testing output JSON.
    Expected: {
        window_id: {
            "symbols": list[str],
            "strategy": str,
            "test": {
                "params": dict,
                "transactions": list,
                "metrics": dict,
            },
            "window": {
                "start_date": str,
                "end_date": str,
                "window_id": str
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
        # Check for required keys at the top level
        for key in ["symbols", "strategy", "test", "window"]:
            if key not in window_data:
                logger.warning(
                    f"Validation failed: '{key}' missing at top level. Id: {window_id}, Data: {window_data}"
                )
                return False
        # Validate symbols
        if not isinstance(window_data["symbols"], list) or not all(
            isinstance(s, str) for s in window_data["symbols"]
        ):
            logger.warning(
                f"Validation failed: 'symbols' not a list of str. Id: {window_id}, Value: {window_data['symbols']}"
            )
            return False
        # Validate strategy
        if not isinstance(window_data["strategy"], str):
            logger.warning(
                f"Validation failed: 'strategy' not str. Id: {window_id}, Value: {window_data['strategy']}"
            )
            return False
        # Validate test section
        test = window_data["test"]
        if not isinstance(test, dict):
            logger.warning(
                f"Validation failed: 'test' not dict. Id: {window_id}, Value: {test}"
            )
            return False
        for key in ["params", "transactions", "metrics"]:
            if key not in test:
                logger.warning(
                    f"Validation failed: '{key}' missing in test. Id: {window_id}, Data: {test}"
                )
                return False
        if not isinstance(test["params"], dict):
            logger.warning(
                f"Validation failed: 'params' not dict in test. Id: {window_id}, Value: {test['params']}"
            )
            return False
        if not isinstance(test["transactions"], list):
            logger.warning(
                f"Validation failed: 'transactions' not list in test. Id: {window_id}, Value: {test['transactions']}"
            )
            return False
        if not isinstance(test["metrics"], dict):
            logger.warning(
                f"Validation failed: 'metrics' not dict in test. Id: {window_id}, Value: {test['metrics']}"
            )
            return False
        # Validate window section
        win = window_data["window"]
        if not isinstance(win, dict):
            logger.warning(
                f"Validation failed: 'window' not dict. Id: {window_id}, Value: {win}"
            )
            return False
        for date_key in ["start_date", "end_date", "window_id"]:
            if date_key not in win or not isinstance(win[date_key], str):
                logger.warning(
                    f"Validation failed: '{date_key}' missing or not str in window. Id: {window_id}, Value: {win}"
                )
                return False
    return True


def validate_portfolio_optimization_testing_stage_coordinator_input(
    input_data: dict, logger: Loggable
) -> bool:
    """
    Validate the input structure for portfolio optimization results (single strategy, single symbol).
    Expected: {
        window_id: {
            "strategy": str,
            "symbols": list[str],
            "optimization": dict,
            "window": {
                "start_date": str,
                "end_date": str,
                "window_id": str
            }
        }
    }
    """
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
        # Must have 'strategy', 'symbols', 'optimization', and 'window'
        for key in ["strategy", "symbols", "optimization", "window"]:
            if key not in window_data:
                logger.warning(
                    f"Validation failed: '{key}' missing in window_data. Window ID: {window_id}, Value: {window_data}"
                )
                return False
        # Validate strategy
        if not isinstance(window_data["strategy"], str):
            logger.warning(
                f"Validation failed: 'strategy' not str in window_data. Window ID: {window_id}, Value: {window_data['strategy']}"
            )
            return False
        # Validate symbols
        if not isinstance(window_data["symbols"], list) or not all(
            isinstance(s, str) for s in window_data["symbols"]
        ):
            logger.warning(
                f"Validation failed: 'symbols' not a list of str in window_data. Window ID: {window_id}, Value: {window_data['symbols']}"
            )
            return False
        # Validate optimization section
        optimization = window_data["optimization"]
        if not isinstance(optimization, dict):
            logger.warning(
                f"Validation failed: 'optimization' is not a dict. Window ID: {window_id}, Value: {optimization}"
            )
            return False
        # Validate window section
        win = window_data["window"]
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
