from enum import Enum

from algo_royale.backtester.stage_data_validation.portfolio_backtest_executor_validator import (
    validate_portfolio_backtest_executor_input,
    validate_portfolio_backtest_executor_output,
)
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
from algo_royale.backtester.stage_data_validation.validate_asyn_iterator_dict import (
    validate_portfolio_optimization_stage_coordinator_input,
    validate_signal_strategy_backtest_executor_input,
    validate_signal_strategy_backtest_executor_output,
)


class BacktestStageDictValidation(Enum):
    """
    Enum for validating the structure of backtest stage dictionaries.
    Each member corresponds to a specific validation rule for the dictionary.
    """

    # Signal Strategy Backtest Executor
    SIGNAL_BACKTEST_EVALUATOR = signal_backtest_evaluator_validator
    # Signal Strategy Backtest Executor
    SIGNAL_BACKTEST_EXECUTOR_INPUT = validate_signal_strategy_backtest_executor_input
    SIGNAL_BACKTEST_EXECUTOR_OUTPUT = validate_signal_strategy_backtest_executor_output
    # Signal Strategy Optimization and Testing
    STRATEGY_OPTIMIZATION_OUTPUT = signal_strategy_optimization_result_validator
    STRATEGY_TESTING_OUTPUT = signal_strategy_testing_validator
    STRATEGY_OPTIMIZATION_TESTING = signal_strategy_full_result_validator
    # Signal Strategy Evaluation
    SIGNAL_STRATEGY_EVALUATION = signal_evaluation_result_validator
    SIGNAL_SYMBOL_EVALUATION = signal_summary_validator

    # Portfolio Backtest Executor
    PORTFOLIO_BACKTEST_EXECUTOR_INPUT = validate_portfolio_backtest_executor_input
    PORTFOLIO_BACKTEST_EXECUTOR_OUTPUT = validate_portfolio_backtest_executor_output
    # Portfolio Optimization and Testing
    PORTFOLIO_OPTIMIZATION_INPUT = (
        validate_portfolio_optimization_stage_coordinator_input
    )
    PORTFOLIO_OPTIMIZATION_OUTPUT = (
        validate_portfolio_optimization_stage_coordinator_output
    )
