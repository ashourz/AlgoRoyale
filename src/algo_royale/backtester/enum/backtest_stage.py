from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, List, Optional

from algo_royale.backtester.column_names.data_ingest_columns import DataIngestColumns
from algo_royale.backtester.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)
from algo_royale.backtester.column_names.portfolio_strategy_columns import (
    PortfolioStrategyInputColumns,
    PortfolioStrategyOutputColumns,
)
from algo_royale.backtester.column_names.strategy_columns import (
    SignalStrategyColumns,
)
from algo_royale.backtester.enum.backtest_stage_dict_validation import (
    BacktestStageDictValidation,
)


class BacktestStageName(str):
    DATA_INGEST = "data_ingest"
    FEATURE_ENGINEERING = "feature_engineering"
    ##SIGNAL
    SIGNAL_STRATEGY = "signal_strategy"
    SIGNAL_BACKTEST_EXECUTOR = "signal_backtest_executor"
    SIGNAL_BACKTEST_EVALUATOR = "signal_backtest_evaluator"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    STRATEGY_TESTING = "strategy_testing"
    STRATEGY_EVALUATION = "strategy_evaluation"
    SYMBOL_EVALUATION = "symbol_evaluation"
    ##PORTFOLIO
    PORTFOLIO_STRATEGY = "portfolio_strategy"
    PORTFOLIO_BACKTEST_EXECUTOR = "portfolio_backtest_executor"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    PORTFOLIO_TESTING = "portfolio_testing"
    PORTFOLIO_EVALUATION = "portfolio_evaluation"
    ##WALK FORWARD
    SIGNAL_STRATEGY_WALK_FORWARD = "signal_strategy_walk_forward"
    PORTFOLIO_STRATEGY_WALK_FORWARD = "portfolio_strategy_walk_forward"


@dataclass(frozen=True)
class BaseStageDef:
    value: str
    description: str
    input_stage_name: Optional[str]


@dataclass(frozen=True)
class TabularStageDef(BaseStageDef):
    input_columns: List[str]
    output_columns: List[str]


@dataclass(frozen=True)
class OutputMetricValidationStageDef(BaseStageDef):
    input_columns: List[str]
    output_metric_validation_fn: Callable[[Any], bool]


@dataclass(frozen=True)
class InputOutputMetricValidationStageDef(BaseStageDef):
    input_columns: List[str]
    input_metric_validation_fn: Callable[[Any], bool]
    output_metric_validation_fn: Callable[[Any], bool]


@dataclass(frozen=True)
class FullMetricValidationStageDef(BaseStageDef):
    input_validation_fn: Callable[[Any], bool]
    output_data_validation_fn: Callable[[Any], bool]


class BacktestStage(Enum):
    """
    Enum representing the different stages of the pipeline.
    Each stage has a value, description, required columns, and a rename map.
    """

    DATA_INGEST = TabularStageDef(
        value=BacktestStageName.DATA_INGEST,
        description="Loading and staging raw/unprocessed data (from API, files, DB, etc.)",
        input_stage_name=None,
        input_columns=DataIngestColumns.get_all_column_values(),
        output_columns=DataIngestColumns.get_all_column_values(),
    )
    FEATURE_ENGINEERING = TabularStageDef(
        value=BacktestStageName.FEATURE_ENGINEERING,
        description="Creating new features from existing data (technical indicators, etc.)",
        input_stage_name=BacktestStageName.DATA_INGEST,
        input_columns=DataIngestColumns.get_all_column_values(),
        output_columns=FeatureEngineeringColumns.get_all_column_values(),
    )
    ## SIGNAL
    SIGNAL_STRATEGY = TabularStageDef(
        value=BacktestStageName.SIGNAL_STRATEGY,
        description="Defining trading strategies based on signals",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=FeatureEngineeringColumns.get_all_column_values(),
        output_columns=SignalStrategyColumns.get_all_column_values(),
    )
    SIGNAL_BACKTEST_EXECUTOR = FullMetricValidationStageDef(
        value=BacktestStageName.SIGNAL_BACKTEST_EXECUTOR,
        description="Executing backtests for individual trading strategies",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_validation_fn=BacktestStageDictValidation.SIGNAL_BACKTEST_EXECUTOR_INPUT,
        output_data_validation_fn=BacktestStageDictValidation.SIGNAL_BACKTEST_EXECUTOR_OUTPUT,
    )
    SIGNAL_BACKTEST_EVALUATOR = OutputMetricValidationStageDef(
        value=BacktestStageName.SIGNAL_BACKTEST_EVALUATOR,
        description="Evaluating backtest results for individual trading strategies",
        input_stage_name=BacktestStageName.SIGNAL_STRATEGY,
        input_columns=FeatureEngineeringColumns.get_all_column_values(),
        output_metric_validation_fn=BacktestStageDictValidation.SIGNAL_BACKTEST_EVALUATOR,
    )
    STRATEGY_OPTIMIZATION = OutputMetricValidationStageDef(
        value=BacktestStageName.STRATEGY_OPTIMIZATION,
        description="Optimizing strategies using historical data",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=FeatureEngineeringColumns.get_all_column_values(),
        output_metric_validation_fn=BacktestStageDictValidation.STRATEGY_OPTIMIZATION_OUTPUT,
    )
    STRATEGY_TESTING = InputOutputMetricValidationStageDef(
        value=BacktestStageName.STRATEGY_TESTING,
        description="Testing strategies using historical data",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=FeatureEngineeringColumns.get_all_column_values(),
        input_metric_validation_fn=BacktestStageDictValidation.STRATEGY_OPTIMIZATION_OUTPUT,
        output_metric_validation_fn=BacktestStageDictValidation.STRATEGY_TESTING_OUTPUT,
    )
    STRATEGY_EVALUATION = FullMetricValidationStageDef(
        value=BacktestStageName.STRATEGY_EVALUATION,
        description="Evaluating strategies based on performance metrics",
        input_stage_name=None,
        input_validation_fn=BacktestStageDictValidation.STRATEGY_OPTIMIZATION_TESTING_OUTPUT,
        output_data_validation_fn=BacktestStageDictValidation.SIGNAL_STRATEGY_EVALUATION,
    )
    SYMBOL_EVALUATION = FullMetricValidationStageDef(
        value=BacktestStageName.SYMBOL_EVALUATION,
        description="Evaluating symbols based on performance metrics",
        input_stage_name=None,
        input_validation_fn=BacktestStageDictValidation.SIGNAL_STRATEGY_EVALUATION,
        output_data_validation_fn=BacktestStageDictValidation.SIGNAL_SYMBOL_EVALUATION,
    )
    ## PORTFOLIO
    PORTFOLIO_STRATEGY = TabularStageDef(
        value=BacktestStageName.PORTFOLIO_STRATEGY,
        description="Defining portfolio strategies based on multiple signal strategies",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=PortfolioStrategyInputColumns.get_all_column_values(),
        output_columns=PortfolioStrategyOutputColumns.get_all_column_values(),
    )
    PORTFOLIO_BACKTEST_EXECUTOR = FullMetricValidationStageDef(
        value=BacktestStageName.PORTFOLIO_BACKTEST_EXECUTOR,
        description="Executing backtests for a portfolio of strategies",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_validation_fn=BacktestStageDictValidation.PORTFOLIO_BACKTEST_EXECUTOR_INPUT,
        output_data_validation_fn=BacktestStageDictValidation.PORTFOLIO_BACKTEST_EXECUTOR_OUTPUT,
    )
    PORTFOLIO_OPTIMIZATION = FullMetricValidationStageDef(
        value=BacktestStageName.PORTFOLIO_OPTIMIZATION,
        description="Optimizing a portfolio of strategies",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_validation_fn=BacktestStageDictValidation.PORTFOLIO_OPTIMIZATION_INPUT,
        output_data_validation_fn=BacktestStageDictValidation.PORTFOLIO_OPTIMIZATION_OUTPUT,
    )
    PORTFOLIO_TESTING = FullMetricValidationStageDef(
        value=BacktestStageName.PORTFOLIO_TESTING,
        description="Testing a portfolio of strategies on historical data",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_validation_fn=BacktestStageDictValidation.PORTFOLIO_TESTING_INPUT,
        output_data_validation_fn=BacktestStageDictValidation.PORTFOLIO_TESTING_OUTPUT,
    )
    PORTFOLIO_EVALUATION = FullMetricValidationStageDef(
        value=BacktestStageName.PORTFOLIO_EVALUATION,
        description="Evaluating a portfolio of strategies based on performance metrics",
        input_stage_name=None,
        input_validation_fn=BacktestStageDictValidation.PORTFOLIO_EVALUATION_INPUT,
        output_data_validation_fn=BacktestStageDictValidation.PORTFOLIO_EVALUATION_OUTPUT,
    )
    ## WALK FORWARD
    # SIGNAL_STRATEGY_WALK_FORWARD = BacktestStageDef(
    #     value=BacktestStageName.SIGNAL_STRATEGY_WALK_FORWARD,
    #     description="Walk forward evaluation of signal strategies",
    #     input_stage_name=BacktestStageName.SIGNAL_BACKTEST_EVALUATOR,
    #     input_columns=[],
    #     output_columns=[],
    # )
    # PORTFOLIO_STRATEGY_WALK_FORWARD = BacktestStageDef(
    #     value=BacktestStageName.PORTFOLIO_STRATEGY_WALK_FORWARD,
    #     description="Walk forward evaluation of portfolio strategies",
    #     input_stage_name=BacktestStageName.PORTFOLIO_BACKTEST_EXECUTOR,
    #     input_columns=[],
    #     output_columns=[],
    # )

    @property
    def input_stage(self) -> Optional["BacktestStage"]:
        """
        Returns the BacktestStage enum member corresponding to this stage's input_stage_name, if any.
        """
        if self.value.input_stage_name is None:
            return None
        return BacktestStage.get_stage_by_name(self.value.input_stage_name)

    @property
    def name(self) -> str:
        """
        Returns the string value of the BacktestStage.
        """
        return self.value.value

    @classmethod
    def get_stage_by_name(cls, name: str) -> Optional["BacktestStage"]:
        for stage in cls:
            if stage.name == name:
                return stage
        return None
