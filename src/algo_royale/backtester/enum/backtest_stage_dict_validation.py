from enum import Enum

from algo_royale.backtester.stage_data_validation.portfolio_backtest_executor_validator import (
    validate_portfolio_backtest_executor_input,
    validate_portfolio_backtest_executor_output,
)
from algo_royale.backtester.stage_data_validation.portfolio_evaluation_coordinator_validator import (
    validate_portfolio_evaluation_input_json,
    validate_portfolio_evaluation_output_json,
)
from algo_royale.backtester.stage_data_validation.portfolio_optimization_stage_coordinator_validator import (
    validate_portfolio_optimization_json_output,
)
from algo_royale.backtester.stage_data_validation.portfolio_testing_stage_coordinator_validator import (
    validate_portfolio_testing_json_output,
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
    validate_portfolio_optimization_testing_stage_coordinator_input,
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
    """ Validator for the output of the signal backtest evaluator stage."""
    # Signal Strategy Backtest Executor
    SIGNAL_BACKTEST_EXECUTOR_INPUT = validate_signal_strategy_backtest_executor_input
    """ Validator for the input of the signal backtest executor stage."""
    SIGNAL_BACKTEST_EXECUTOR_OUTPUT = validate_signal_strategy_backtest_executor_output
    """ Validator for the output of the signal backtest executor stage."""
    # Signal Strategy Optimization and Testing
    STRATEGY_OPTIMIZATION_OUTPUT = signal_strategy_optimization_result_validator
    """ Validator for the output of the signal strategy optimization stage."""
    STRATEGY_TESTING_OUTPUT = signal_strategy_testing_validator
    """ Validator for the output of the signal strategy testing stage."""
    STRATEGY_OPTIMIZATION_TESTING = signal_strategy_full_result_validator
    """ Validator for the combined output of the signal strategy optimization and testing stages."""
    # Signal Strategy Evaluation
    SIGNAL_STRATEGY_EVALUATION = signal_evaluation_result_validator
    """ Validator for the output of the signal strategy evaluation stage."""
    SIGNAL_SYMBOL_EVALUATION = signal_summary_validator
    """ Validator for the output of the signal symbol evaluation stage."""

    # Portfolio Backtest Executor
    PORTFOLIO_BACKTEST_EXECUTOR_INPUT = validate_portfolio_backtest_executor_input
    """ Validator for the input of the portfolio backtest executor stage."""
    PORTFOLIO_BACKTEST_EXECUTOR_OUTPUT = validate_portfolio_backtest_executor_output
    """ Validator for the output of the portfolio backtest executor stage."""
    # Portfolio Optimization and Testing
    PORTFOLIO_OPTIMIZATION_INPUT = (
        validate_portfolio_optimization_testing_stage_coordinator_input
    )
    """ Validator for the input of the portfolio optimization stage."""
    PORTFOLIO_OPTIMIZATION_OUTPUT = validate_portfolio_optimization_json_output
    """ Validator for the output of the portfolio optimization stage."""
    PORTFOLIO_TESTING_INPUT = (
        validate_portfolio_optimization_testing_stage_coordinator_input
    )
    """ Validator for the input of the portfolio testing stage."""
    PORTFOLIO_TESTING_OUTPUT = validate_portfolio_testing_json_output
    """ Validator for the output of the portfolio testing stage."""
    PORTFOLIO_EVALUATION_INPUT = validate_portfolio_evaluation_input_json
    """ Validator for the input of the portfolio evaluation stage."""
    PORTFOLIO_EVALUATION_OUTPUT = validate_portfolio_evaluation_output_json
    """ Validator for the output of the portfolio evaluation stage."""
