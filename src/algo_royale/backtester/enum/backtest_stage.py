from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from algo_royale.backtester.column_names.data_ingest_columns import DataIngestColumns
from algo_royale.backtester.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)


class BacktestStageName(str):
    DATA_INGEST = "data_ingest"
    FEATURE_ENGINEERING = "feature_engineering"
    ##SIGNAL
    SIGNAL_BACKTEST_EXECUTOR = "signal_backtest_executor"
    SIGNAL_BACKTEST_EVALUATOR = "signal_backtest_evaluator"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    STRATEGY_TESTING = "strategy_testing"
    STRATEGY_EVALUATION = "strategy_evaluation"
    SYMBOL_EVALUATION = "symbol_evaluation"
    ##PORTFOLIO
    PORTFOLIO_BACKTEST_EXECUTOR = "portfolio_backtest_executor"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    PORTFOLIO_TESTING = "portfolio_testing"
    PORTFOLIO_EVALUATION = "portfolio_evaluation"
    ##WALK FORWARD
    SIGNAL_STRATEGY_WALK_FORWARD = "signal_strategy_walk_forward"
    PORTFOLIO_STRATEGY_WALK_FORWARD = "portfolio_strategy_walk_forward"


@dataclass(frozen=True)
class BacktestStageDef:
    value: str
    description: str
    input_stage_name: Optional[str]
    input_columns: List[str]
    output_columns: List[str]


class BacktestStage(Enum):
    """
    Enum representing the different stages of the pipeline.
    Each stage has a value, description, required columns, and a rename map.
    """

    DATA_INGEST = BacktestStageDef(
        value=BacktestStageName.DATA_INGEST,
        description="Loading and staging raw/unprocessed data (from API, files, DB, etc.)",
        input_stage_name=None,
        input_columns=DataIngestColumns.get_all_column_values(),
        output_columns=DataIngestColumns.get_all_column_values(),
    )
    FEATURE_ENGINEERING = BacktestStageDef(
        value=BacktestStageName.FEATURE_ENGINEERING,
        description="Creating new features from existing data (technical indicators, etc.)",
        input_stage_name=BacktestStageName.DATA_INGEST,
        input_columns=DataIngestColumns.get_all_column_values(),
        output_columns=FeatureEngineeringColumns.get_all_column_values(),
    )
    ## SIGNAL
    SIGNAL_BACKTEST_EXECUTOR = BacktestStageDef(
        value=BacktestStageName.SIGNAL_BACKTEST_EXECUTOR,
        description="Executing backtests for individual trading strategies",
        input_stage_name=None,
        input_columns=[],
        output_columns=[],
    )
    SIGNAL_BACKTEST_EVALUATOR = BacktestStageDef(
        value=BacktestStageName.SIGNAL_BACKTEST_EVALUATOR,
        description="Evaluating backtest results for individual trading strategies",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=[],
        output_columns=[],
    )
    STRATEGY_OPTIMIZATION = BacktestStageDef(
        value=BacktestStageName.STRATEGY_OPTIMIZATION,
        description="Optimizing strategies using historical data",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=FeatureEngineeringColumns.get_all_column_values(),
        output_columns=[],
    )
    STRATEGY_TESTING = BacktestStageDef(
        value=BacktestStageName.STRATEGY_TESTING,
        description="Testing strategies using historical data",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=FeatureEngineeringColumns.get_all_column_values(),
        output_columns=[],
    )
    STRATEGY_EVALUATION = BacktestStageDef(
        value=BacktestStageName.STRATEGY_EVALUATION,
        description="Evaluating strategies based on performance metrics",
        input_stage_name=None,
        input_columns=[],
        output_columns=[],
    )
    SYMBOL_EVALUATION = BacktestStageDef(
        value=BacktestStageName.SYMBOL_EVALUATION,
        description="Evaluating symbols based on performance metrics",
        input_stage_name=None,
        input_columns=[],
        output_columns=[],
    )
    ## PORTFOLIO
    PORTFOLIO_BACKTEST_EXECUTOR = BacktestStageDef(
        value=BacktestStageName.PORTFOLIO_BACKTEST_EXECUTOR,
        description="Executing backtests for a portfolio of strategies",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=[],
        output_columns=[],
    )
    PORTFOLIO_OPTIMIZATION = BacktestStageDef(
        value=BacktestStageName.PORTFOLIO_OPTIMIZATION,
        description="Optimizing a portfolio of strategies",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=FeatureEngineeringColumns.get_all_column_values(),
        output_columns=[],
    )
    PORTFOLIO_TESTING = BacktestStageDef(
        value=BacktestStageName.PORTFOLIO_TESTING,
        description="Testing a portfolio of strategies on historical data",
        input_stage_name=BacktestStageName.FEATURE_ENGINEERING,
        input_columns=FeatureEngineeringColumns.get_all_column_values(),
        output_columns=[],
    )
    PORTFOLIO_EVALUATION = BacktestStageDef(
        value=BacktestStageName.PORTFOLIO_EVALUATION,
        description="Evaluating a portfolio of strategies based on performance metrics",
        input_stage_name=None,
        input_columns=[],
        output_columns=[],
    )
    ## WALK FORWARD
    SIGNAL_STRATEGY_WALK_FORWARD = BacktestStageDef(
        value=BacktestStageName.SIGNAL_STRATEGY_WALK_FORWARD,
        description="Walk forward evaluation of signal strategies",
        input_stage_name=BacktestStageName.SIGNAL_BACKTEST_EVALUATOR,
        input_columns=[],
        output_columns=[],
    )
    PORTFOLIO_STRATEGY_WALK_FORWARD = BacktestStageDef(
        value=BacktestStageName.PORTFOLIO_STRATEGY_WALK_FORWARD,
        description="Walk forward evaluation of portfolio strategies",
        input_stage_name=BacktestStageName.PORTFOLIO_BACKTEST_EXECUTOR,
        input_columns=[],
        output_columns=[],
    )

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
