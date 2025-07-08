def validate_portfolio_optimization_json_output(output: dict) -> bool:
    """
    Validate the structure of a portfolio optimization output JSON.
    """
    if not isinstance(output, dict):
        return False
    for window_id, window_data in output.items():
        if not isinstance(window_id, str) or not isinstance(window_data, dict):
            return False
        # Check for required keys
        if "optimization" not in window_data or "window" not in window_data:
            return False
        opt = window_data["optimization"]
        win = window_data["window"]
        # Validate optimization section
        if not isinstance(opt, dict):
            return False
        for key in ["strategy", "best_value", "best_params", "meta", "metrics"]:
            if key not in opt:
                return False
        if not isinstance(opt["strategy"], str):
            return False
        if not (
            isinstance(opt["best_value"], (float, int))
            or opt["best_value"] in [float("inf"), float("-inf")]
        ):
            return False
        if not isinstance(opt["best_params"], dict):
            return False
        if not isinstance(opt["meta"], dict):
            return False
        for meta_key in [
            "run_time_sec",
            "n_trials",
            "symbol",
            "direction",
            "multi_objective",
        ]:
            if meta_key not in opt["meta"]:
                return False
        if not isinstance(opt["metrics"], dict):
            return False
        # Validate window section
        if not isinstance(win, dict):
            return False
        for date_key in ["start_date", "end_date"]:
            if date_key not in win or not isinstance(win[date_key], str):
                return False
    return True
