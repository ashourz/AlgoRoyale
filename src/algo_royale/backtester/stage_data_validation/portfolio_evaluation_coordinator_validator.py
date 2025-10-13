from typing import Any, Dict
from algo_royale.logging.loggable import Loggable


def validate_portfolio_evaluation_input_json(
    output: Dict[str, Any], logger: Loggable
) -> bool:
    """
    Validate that the input JSON for PortfolioEvaluationCoordinator contains both
    valid optimization and testing structures for each window.
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
        # Must have a window section
        if "window" not in window_data or not isinstance(window_data["window"], dict):
            logger.warning(
                f"Validation failed: 'window' missing or not dict. Id: {window_id}, Data: {window_data}"
            )
            return False
        for date_key in ["start_date", "end_date"]:
            if date_key not in window_data["window"] or not isinstance(
                window_data["window"][date_key], str
            ):
                logger.warning(
                    f"Validation failed: '{date_key}' missing or not str in window. Id: {window_id}, Data: {window_data['window']}"
                )
                return False
        # Must have at least one of optimization or test
        has_optimization = "optimization" in window_data and isinstance(
            window_data["optimization"], dict
        )
        has_test = "test" in window_data and isinstance(window_data["test"], dict)
        if not (has_optimization and has_test):
            logger.warning(
                f"Validation failed: Missing optimization or test section. Id: {window_id}, Data: {window_data}"
            )
            return False
        # Validate optimization section
        opt = window_data["optimization"]
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
        if not isinstance(opt["metrics"], dict) or "metrics" not in opt["metrics"]:
            logger.warning(
                f"Validation failed: 'metrics' not dict or missing 'metrics' key in optimization. Id: {window_id}, Value: {opt['metrics']}"
            )
            return False
        # Validate test section
        test = window_data["test"]
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
    return True


def validate_portfolio_evaluation_output_json(output: dict, logger: Loggable) -> bool:
    """
    Validate the structure of the output JSON produced by PortfolioEvaluationCoordinator.
    Expected: {symbol: { ...summary fields... }}
    """
    if not isinstance(output, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {output}")
        return False
    for symbol, summary in output.items():
        if not isinstance(symbol, str) or not isinstance(summary, dict):
            logger.warning(
                f"Validation failed: Symbol not str or summary not dict. Symbol: {symbol}, Summary: {summary}"
            )
            return False
        required_keys = [
            "symbol",
            "recommended_strategy",
            "viability_score",
            "param_consistency",
            "metrics",
            "allocation_params",
            "rationale",
        ]
        for key in required_keys:
            if key not in summary:
                logger.warning(
                    f"Validation failed: '{key}' missing in summary. Symbol: {symbol}, Summary: {summary}"
                )
                return False
        if not isinstance(summary["symbol"], str):
            logger.warning(
                f"Validation failed: 'symbol' not str in summary. Symbol: {symbol}, Value: {summary['symbol']}"
            )
            return False
        if not isinstance(summary["recommended_strategy"], str):
            logger.warning(
                f"Validation failed: 'recommended_strategy' not str in summary. Symbol: {symbol}, Value: {summary['recommended_strategy']}"
            )
            return False
        # viability_score and param_consistency can be float or None
        if summary["viability_score"] is not None and not isinstance(
            summary["viability_score"], (float, int)
        ):
            logger.warning(
                f"Validation failed: 'viability_score' not float/int in summary. Symbol: {symbol}, Value: {summary['viability_score']}"
            )
            return False
        if summary["param_consistency"] is not None and not isinstance(
            summary["param_consistency"], (float, int)
        ):
            logger.warning(
                f"Validation failed: 'param_consistency' not float/int in summary. Symbol: {symbol}, Value: {summary['param_consistency']}"
            )
            return False
        if not isinstance(summary["metrics"], dict):
            logger.warning(
                f"Validation failed: 'metrics' not dict in summary. Symbol: {symbol}, Value: {summary['metrics']}"
            )
            return False
        if not isinstance(summary["allocation_params"], dict):
            logger.warning(
                f"Validation failed: 'allocation_params' not dict in summary. Symbol: {symbol}, Value: {summary['allocation_params']}"
            )
            return False
        if not isinstance(summary["rationale"], str):
            logger.warning(
                f"Validation failed: 'rationale' not str in summary. Symbol: {symbol}, Value: {summary['rationale']}"
            )
            return False
    return True
