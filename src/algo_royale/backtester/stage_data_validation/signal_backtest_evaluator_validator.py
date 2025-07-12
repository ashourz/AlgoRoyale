from algo_royale.logging.loggable import Loggable
# Define the validation function outside the Enum


def signal_backtest_evaluator_validator(d: dict, logger: Loggable) -> bool:
    """Validate the structure of a backtest stage dictionary for signal backtest evaluation."""
    if not isinstance(d, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {d}")
        return False
    for k in ["total_return", "sharpe_ratio", "win_rate", "max_drawdown"]:
        if k not in d:
            logger.warning(f"Validation failed: '{k}' missing. Value: {d}")
            return False
        if not isinstance(d[k], float):
            logger.warning(f"Validation failed: '{k}' not float. Value: {d[k]}")
            return False
    return True
