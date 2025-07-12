from algo_royale.backtester.stage_data_validation.signal_strategy_optimization_result_validator import (
    window_section_validator,
)
from algo_royale.logging.loggable import Loggable


def signal_strategy_full_result_validator(d, logger: Loggable) -> bool:
    """
    Validate the structure of the full signal strategy result dictionary,
    as found in optimization_result.json (including 'test', 'optimization', and 'window' keys).
    Allows either 'test' or 'optimization' to be missing for a window, but 'window' must always be present.
    Fails if both 'test' and 'optimization' are missing.
    """
    if not isinstance(d, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {d}")
        return False
    for window_key, window_val in d.items():
        if not isinstance(window_val, dict):
            logger.warning(
                f"Validation failed: Window value not dict. Key: {window_key}, Value: {window_val}"
            )
            return False
        # 'window' must always be present
        if "window" not in window_val:
            logger.warning(
                f"Validation failed: 'window' missing in window value. Key: {window_key}, Value: {window_val}"
            )
            return False
        # If both 'test' and 'optimization' are missing, fail
        if "test" not in window_val and "optimization" not in window_val:
            logger.warning(
                f"Validation failed: Both 'test' and 'optimization' missing in window value. Key: {window_key}, Value: {window_val}"
            )
            return False
        # Fill missing 'test' or 'optimization' with empty dicts for validation
        for k in ["test", "optimization"]:
            if k not in window_val:
                logger.info(
                    f"Section '{k}' missing in window '{window_key}', filling with empty dict for validation."
                )
                # This can be an issue but it should not fail validation
        # Validate "window" section
        if not window_section_validator(window_val["window"], logger):
            logger.warning(
                f"Validation failed: 'window' section invalid. Key: {window_key}, Value: {window_val['window']}"
            )
            return False
    return True
