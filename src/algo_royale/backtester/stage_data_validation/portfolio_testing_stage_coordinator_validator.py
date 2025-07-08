def validate_portfolio_testing_json_output(output: dict) -> bool:
    """
    Validate the structure of a portfolio testing output JSON.
    Expected: {window_id: {"test": {"metrics": dict, "transactions": list}, "window": {"start_date": str, "end_date": str}}}
    """
    print("DEBUG: Entering validate_portfolio_testing_json_output function.")
    print("DEBUG: Output data:", output)

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


def validate_portfolio_optimization_testing_stage_coordinator_input(
    input_data: dict,
) -> bool:
    """Validate the input structure for portfolio optimization testing stage."""
    try:
        print(
            "DEBUG: Entering validate_portfolio_optimization_testing_stage_coordinator_input function."
        )
        print("DEBUG: Input data:", input_data)
        if not isinstance(input_data, dict):
            print("DEBUG: Validation failed: input_data is not a dictionary.")
            return False
        for key, value in input_data.items():
            print("DEBUG: Key:", key, "Value:", value)
            if not isinstance(key, str):
                print("DEBUG: Validation failed: key is not a string.")
                return False
            if not isinstance(value, dict):
                print("DEBUG: Validation failed: value is not a dictionary.")
                return False
            if "optimization" not in value:
                print("DEBUG: Validation failed: 'optimization' key missing in value.")
                return False
            if not isinstance(value["optimization"], dict):
                print("DEBUG: Validation failed: 'optimization' is not a dictionary.")
                return False
            optimization = value["optimization"]
            print("DEBUG: Optimization:", optimization)
            if not isinstance(optimization.get("best_params"), dict):
                print("DEBUG: Validation failed: 'best_params' is not a dictionary.")
                return False
            print("DEBUG: Best Params Content:", optimization.get("best_params"))
            if not isinstance(optimization.get("metrics"), dict):
                print("DEBUG: Validation failed: 'metrics' is not a dictionary.")
                return False
            print("DEBUG: Metrics Content:", optimization.get("metrics"))
            if "window" in value:
                window = value["window"]
                print("DEBUG: Validating window:", window)
                if not isinstance(window, dict):
                    print("DEBUG: Validation failed: 'window' is not a dictionary.")
                    return False
                for date_key in ["start_date", "end_date"]:
                    if date_key not in window:
                        print(
                            f"DEBUG: Validation failed: '{date_key}' key missing in window."
                        )
                        return False
                    if not isinstance(window[date_key], str):
                        print(
                            f"DEBUG: Validation failed: '{date_key}' is not a string."
                        )
                        return False
                    print(f"DEBUG: Window {date_key} Content:", window[date_key])
        print("DEBUG: Input data structure matches expected format.")
        return True
    except Exception as e:
        print(f"ERROR: Exception occurred during validation: {e}")
        return False
