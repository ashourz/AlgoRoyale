from algo_royale.backtester.stage_data_validation.signal_strategy_optimization_result_validator import (
    signal_strategy_optimization_validator,
    window_section_validator,
)
from algo_royale.backtester.stage_data_validation.signal_strategy_testing_result_validator import (
    signal_strategy_testing_validator,
)


def signal_strategy_full_result_validator(d) -> bool:
    """
    Validate the structure of the full signal strategy result dictionary,
    as found in optimization_result.json (including 'test', 'optimization', and 'window' keys).
    """
    if not isinstance(d, dict):
        return False
    for window_key, window_val in d.items():
        if not isinstance(window_val, dict):
            return False
        # Must have "test", "optimization", and "window" keys
        for k in ["test", "optimization", "window"]:
            if k not in window_val:
                return False
        # Validate "test" section
        if not signal_strategy_testing_validator(window_val["test"]):
            return False
        # Validate "optimization" section
        if not signal_strategy_optimization_validator(window_val["optimization"]):
            return False
        # Validate "window" section
        if not window_section_validator(window_val["window"]):
            return False
    return True
