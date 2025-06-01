from enum import Enum
from typing import Optional

from algo_royale.column_names.data_ingest_columns import DataIngestColumns
from algo_royale.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)


class BacktestStage(Enum):
    """
    Enum representing the different stages of the pipeline.
    Each stage has a value, description, required columns, and a rename map.

    - Attributes:
        value (str): The value of the stage.
        description (str): A description of the stage.
        incoming_stage (Optional[str]): The stage that feeds into this stage.
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

    DATA_INGEST = (
        "data_ingest",
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
        "feature_engineering",
        "Creating new features from existing data (technical indicators, etc.)",
        "DATA_INGEST",
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
    BACKTEST = (
        "backtest",
        "Backtesting strategies on historical data",
        "FEATURE_ENGINEERING",
        [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "symbol",
        ],
        {
            "timestamp": "timestamp",
            "open_price": "open",
            "high_price": "high",
            "low_price": "low",
            "close_price": "close",
            "volume": "volume",
            "num_trades": "num_trades",
            "volume_weighted_price": "volume_weighted_price",
        },
    )
    STRATEGY_OPTIMIZATION = (
        "strategy_optimization",
        "Optimizing strategies using historical data",
        "BACKTEST",
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
        "results_analysis",
        "Analyzing backtest results and performance metrics",
        "STRATEGY_OPTIMIZATION",
        [],
        {},
    )
    STRATEGY_METRICS = (
        "strategy_metrics",
        "Calculating and reporting strategy performance metrics",
        "RESULTS_ANALYSIS",
        [],
        {},
    )
    STRATEGY_SELECTION = (
        "strategy_selection",
        "Selecting the best strategy based on performance metrics",
        "STRATEGY_METRICS",
        [],
        {},
    )
    REPORTING = (
        "reporting",
        "Generating reports and visualizations for analysis",
        "STRATEGY_SELECTION",
        [],
        {},
    )
    DEPLOYMENT = (
        "deployment",
        "Deploying the selected strategy for live trading",
        "REPORTING",
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


# After class definition, resolve incoming_stage
for stage in BacktestStage:
    if isinstance(stage._incoming_stage_name, str):
        stage.incoming_stage = BacktestStage[stage._incoming_stage_name]
    else:
        stage.incoming_stage = None
