from enum import Enum
from typing import Optional

from algo_royale.column_names.data_ingest_columns import DataIngestColumns
from algo_royale.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)


class BacktestStageName(str):
    STRATEGY_WALK_FORWARD = "walk_forward"
    DATA_INGEST = "data_ingest"
    FEATURE_ENGINEERING = "feature_engineering"
    BACKTEST = "backtest"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    OPTIMIZATION = "optimization"
    TESTING = "testing"
    STRATEGY_EVALUATION = "evaluation"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    PORTFOLIO_TESTING = "portfolio_testing"
    PORTFOLIO_EVALUATION = "portfolio_evaluation"

    RESULTS_ANALYSIS = "results_analysis"
    STRATEGY_METRICS = "strategy_metrics"
    STRATEGY_SELECTION = "strategy_selection"
    REPORTING = "reporting"
    DEPLOYMENT = "deployment"


class BacktestStage(Enum):
    """
    Enum representing the different stages of the pipeline.
    Each stage has a value, description, required columns, and a rename map.

    - Attributes:
        value (str): The value of the stage.
        description (str): A description of the stage.
        incoming_stage_name (Optional[str]): The stage that feeds into this stage.
        required_input_columns (list): A list of required columns for the stage.
        rename_map (dict): A dictionary mapping original column names to new names.

    - Stages:
        DATA_INGEST: Loading and staging raw/unprocessed data (from API, files, DB, etc.)
        FEATURE_ENGINEERING: Creating new features from existing data (technical indicators, etc.)
        BACKTEST: Backtesting strategies on historical data
        STRATEGY_OPTIMIZATION: Optimizing strategies using historical data
        RESULTS_ANALYSIS: Analyzing backtest results and performance metrics
        STRATEGY_METRICS: Calculating and reporting strategy performance metrics
        STRATEGY_SELECTION: Selecting the best strategy based on performance metrics
        REPORTING: Generating reports and visualizations for analysis
        DEPLOYMENT: Deploying the selected strategy for live trading
    """

    STRATEGY_WALK_FORWARD = (
        BacktestStageName.STRATEGY_WALK_FORWARD,
        "Walk forward evaluation of strategies",
        None,
        [],
        {},
    )
    DATA_INGEST = (
        BacktestStageName.DATA_INGEST,
        "Loading and staging raw/unprocessed data (from API, files, DB, etc.)",
        None,
        [
            DataIngestColumns.TIMESTAMP,
            DataIngestColumns.OPEN_PRICE,
            DataIngestColumns.HIGH_PRICE,
            DataIngestColumns.LOW_PRICE,
            DataIngestColumns.CLOSE_PRICE,
            DataIngestColumns.VOLUME,
            DataIngestColumns.NUM_TRADES,
            DataIngestColumns.VOLUME_WEIGHTED_PRICE,
            DataIngestColumns.SYMBOL,
        ],
        {},
    )
    FEATURE_ENGINEERING = (
        BacktestStageName.FEATURE_ENGINEERING,
        "Creating new features from existing data (technical indicators, etc.)",
        BacktestStageName.DATA_INGEST,
        [
            FeatureEngineeringColumns.TIMESTAMP,
            FeatureEngineeringColumns.OPEN_PRICE,
            FeatureEngineeringColumns.HIGH_PRICE,
            FeatureEngineeringColumns.LOW_PRICE,
            FeatureEngineeringColumns.CLOSE_PRICE,
            FeatureEngineeringColumns.VOLUME,
            FeatureEngineeringColumns.NUM_TRADES,
            FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE,
            FeatureEngineeringColumns.SYMBOL,
        ],
        {
            DataIngestColumns.TIMESTAMP: FeatureEngineeringColumns.TIMESTAMP,
            DataIngestColumns.OPEN_PRICE: FeatureEngineeringColumns.OPEN_PRICE,
            DataIngestColumns.HIGH_PRICE: FeatureEngineeringColumns.HIGH_PRICE,
            DataIngestColumns.LOW_PRICE: FeatureEngineeringColumns.LOW_PRICE,
            DataIngestColumns.CLOSE_PRICE: FeatureEngineeringColumns.CLOSE_PRICE,
            DataIngestColumns.VOLUME: FeatureEngineeringColumns.VOLUME,
            DataIngestColumns.NUM_TRADES: FeatureEngineeringColumns.NUM_TRADES,
            DataIngestColumns.VOLUME_WEIGHTED_PRICE: FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE,
            DataIngestColumns.SYMBOL: FeatureEngineeringColumns.SYMBOL,
        },
    )
    OPTIMIZATION = (
        BacktestStageName.OPTIMIZATION,
        "Optimizing strategies using historical data",
        BacktestStageName.FEATURE_ENGINEERING,
        [],
        {},
    )
    TESTING = (
        BacktestStageName.TESTING,
        "Testing strategies using historical data",
        BacktestStageName.FEATURE_ENGINEERING,
        [],
        {},
    )
    STRATEGY_EVALUATION = (
        BacktestStageName.STRATEGY_EVALUATION,
        "Evaluating strategies based on performance metrics",
        None,
        [],
        {},
    )
    PORTFOLIO_OPTIMIZATION = (
        BacktestStageName.PORTFOLIO_OPTIMIZATION,
        "Optimizing a portfolio of strategies",
        None,
        [],
        {},
    )
    PORTFOLIO_TESTING = (
        BacktestStageName.PORTFOLIO_TESTING,
        "Testing a portfolio of strategies on historical data",
        None,
        [],
        {},
    )
    PORTFOLIO_EVALUATION = (
        BacktestStageName.PORTFOLIO_EVALUATION,
        "Evaluating a portfolio of strategies based on performance metrics",
        None,
        [],
        {},
    )
    BACKTEST = (
        BacktestStageName.BACKTEST,
        "Backtesting strategies on historical data",
        BacktestStageName.FEATURE_ENGINEERING,
        [],
        {},
    )
    STRATEGY_OPTIMIZATION = (
        BacktestStageName.STRATEGY_OPTIMIZATION,
        "Optimizing strategies using historical data",
        BacktestStageName.BACKTEST,
        [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ],
        {},
    )
    RESULTS_ANALYSIS = (
        BacktestStageName.RESULTS_ANALYSIS,
        "Analyzing backtest results and performance metrics",
        BacktestStageName.STRATEGY_OPTIMIZATION,
        [],
        {},
    )
    STRATEGY_METRICS = (
        BacktestStageName.STRATEGY_METRICS,
        "Calculating and reporting strategy performance metrics",
        BacktestStageName.RESULTS_ANALYSIS,
        [],
        {},
    )
    STRATEGY_SELECTION = (
        BacktestStageName.STRATEGY_SELECTION,
        "Selecting the best strategy based on performance metrics",
        BacktestStageName.STRATEGY_METRICS,
        [],
        {},
    )
    REPORTING = (
        BacktestStageName.REPORTING,
        "Generating reports and visualizations for analysis",
        BacktestStageName.STRATEGY_SELECTION,
        [],
        {},
    )
    DEPLOYMENT = (
        BacktestStageName.DEPLOYMENT,
        "Deploying the selected strategy for live trading",
        BacktestStageName.REPORTING,
        [],
        {},
    )

    def __init__(self, value, description, stage, required_input_columns, rename_map):
        self._value_: str = value
        self.description: str = description
        self._incoming_stage_name: Optional[BacktestStage] = stage
        self.incoming_stage = None  # will be set later
        self.required_input_columns = required_input_columns
        self.rename_map = rename_map


def get_stage_by_name(name: str) -> Optional[BacktestStage]:
    """
    Get a BacktestStage by its name.

    :param name: The name of the stage.
    :return: The BacktestStage if found, otherwise None.
    """
    for stage in BacktestStage:
        if stage.value == name:
            return stage
    return None


# After class definition, resolve incoming_stage
for stage in BacktestStage:
    if isinstance(stage._incoming_stage_name, str):
        stage.incoming_stage = get_stage_by_name(stage._incoming_stage_name)
    else:
        stage.incoming_stage = None
