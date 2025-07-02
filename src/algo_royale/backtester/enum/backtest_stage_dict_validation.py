from enum import Enum

from algo_royale.backtester.stage_data_validation.signal_backtest_evaluator_validator import (
    signal_backtest_evaluator_validator,
)
from algo_royale.backtester.stage_data_validation.signal_strategy_evaluation_validator import (
    signal_evaluation_result_validator,
)
from algo_royale.backtester.stage_data_validation.signal_strategy_full_result_validator import (
    signal_strategy_full_result_validator,
)
from algo_royale.backtester.stage_data_validation.signal_strategy_optimization_result_validator import (
    signal_strategy_optimization_result_validator,
)
from algo_royale.backtester.stage_data_validation.signal_strategy_testing_result_validator import (
    signal_strategy_testing_validator,
)
from algo_royale.backtester.stage_data_validation.signal_summary_validator import (
    signal_summary_validator,
)


class BacktestStageDictValidation(Enum):
    """
    Enum for validating the structure of backtest stage dictionaries.
    Each member corresponds to a specific validation rule for the dictionary.
    """

    SIGNAL_BACKTEST_EVALUATOR = signal_backtest_evaluator_validator
    STRATEGY_OPTIMIZATION = signal_strategy_optimization_result_validator
    STRATEGY_TESTING = signal_strategy_testing_validator
    STRATEGY_OPTIMIZATION_TESTING = signal_strategy_full_result_validator
    SIGNAL_STRATEGY_EVALUATION = signal_evaluation_result_validator
    SIGNAL_SYMBOL_EVALUATION = signal_summary_validator
