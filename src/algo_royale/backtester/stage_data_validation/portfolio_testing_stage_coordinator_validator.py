from algo_royale.logging.loggable import Loggable
def validate_portfolio_testing_json_output(output: dict, logger: Loggable) -> bool:
    """
    Validate the structure of a portfolio testing output JSON.
    Expected: {window_id: {"test": {"metrics": dict, "transactions": list}, "window": {"start_date": str, "end_date": str}}}
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
        if "test" not in window_data or "window" not in window_data:
            logger.warning(
                f"Validation failed: 'test' or 'window' missing. Id: {window_id}, Data: {window_data}"
            )
            return False
        test = window_data["test"]
        win = window_data["window"]
        # Validate test section
        if not isinstance(test, dict):
            logger.warning(
                f"Validation failed: 'test' not dict. Id: {window_id}, Value: {test}"
            )
            return False
        if "metrics" not in test or "transactions" not in test:
            logger.warning(
                f"Validation failed: 'metrics' or 'transactions' missing in test. Id: {window_id}, Data: {test}"
            )
            return False
        if not isinstance(test["metrics"], dict):
            logger.warning(
                f"Validation failed: 'metrics' not dict in test. Id: {window_id}, Value: {test['metrics']}"
            )
            return False
        if not isinstance(test["transactions"], list):
            logger.warning(
                f"Validation failed: 'transactions' not list in test. Id: {window_id}, Value: {test['transactions']}"
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


def validate_portfolio_optimization_testing_stage_coordinator_input(
    input_data: dict, logger: Loggable
) -> bool:
    """Validate the input structure for portfolio optimization testing stage."""
    if not isinstance(input_data, dict):
        logger.warning(
            f"Validation failed: input_data is not a dictionary. Value: {input_data}"
        )
        return False
    for key, value in input_data.items():
        if not isinstance(key, str):
            logger.warning(f"Validation failed: key is not a string. Key: {key}")
            return False
        if not isinstance(value, dict):
            logger.warning(
                f"Validation failed: value is not a dictionary. Key: {key}, Value: {value}"
            )
            return False
        if "optimization" not in value:
            logger.warning(
                f"Validation failed: 'optimization' key missing in value. Key: {key}, Value: {value}"
            )
            return False
        if not isinstance(value["optimization"], dict):
            logger.warning(
                f"Validation failed: 'optimization' is not a dict. Key: {key}, Value: {value['optimization']}"
            )
            return False
    return True
