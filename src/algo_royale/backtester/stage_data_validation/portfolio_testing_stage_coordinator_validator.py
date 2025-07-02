def validate_portfolio_testing_json_output(output: dict) -> bool:
    """
    Validate the structure of a portfolio testing output JSON.
    Expected: {window_id: {"test": {"metrics": dict, "transactions": list}, "window": {"start_date": str, "end_date": str}}}
    """
    if not isinstance(output, dict):
        return False
    for window_id, window_data in output.items():
        if not isinstance(window_id, str) or not isinstance(window_data, dict):
            return False
        # Check for required keys
        if "test" not in window_data or "window" not in window_data:
            return False
        test = window_data["test"]
        win = window_data["window"]
        # Validate test section
        if not isinstance(test, dict):
            return False
        if "metrics" not in test or "transactions" not in test:
            return False
        if not isinstance(test["metrics"], dict):
            return False
        if not isinstance(test["transactions"], list):
            return False
        # Validate window section
        if not isinstance(win, dict):
            return False
        for date_key in ["start_date", "end_date"]:
            if date_key not in win or not isinstance(win[date_key], str):
                return False
    return True
