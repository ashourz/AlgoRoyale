from enum import Enum


##TODO: Fill in remaining stages and their descriptions, required columns, and rename maps
class PipelineStage(Enum):
    """
    Enum representing the different stages of the pipeline.
    Each stage has a value, description, required columns, and a rename map.

    - Attributes:
        value (str): The value of the stage.
        description (str): A description of the stage.
        incoming_stage (Optional[PipelineStage]): The stage that feeds into this stage.
        required_columns (list): A list of required columns for the stage.
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
        None[
            "timestamp",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
            "num_trades",
            "volume_weighted_price",
            "symbol",
        ],
        {},
    )
    FEATURE_ENGINEERING = (
        "feature_engineering",
        "Creating new features from existing data (technical indicators, etc.)",
        DATA_INGEST,
        [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ],
        {
            "open_price": "open",
            "high_price": "high",
            "low_price": "low",
            "close_price": "close",
        },
    )
    BACKTEST = (
        "backtest",
        "Backtesting strategies on historical data",
        FEATURE_ENGINEERING,
        [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "signal",
            "strategy",
            "symbol",
        ],
        {},
    )
    STRATEGY_OPTIMIZATION = (
        "strategy_optimization",
        "Optimizing strategies using historical data",
        BACKTEST,
        [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
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
    RESULTS_ANALYSIS = (
        "results_analysis",
        "Analyzing backtest results and performance metrics",
        STRATEGY_OPTIMIZATION,
        [],
        {},
    )
    STRATEGY_METRICS = (
        "strategy_metrics",
        "Calculating and reporting strategy performance metrics",
        RESULTS_ANALYSIS,
        [],
        {},
    )
    STRATEGY_SELECTION = (
        "strategy_selection",
        "Selecting the best strategy based on performance metrics",
        STRATEGY_METRICS,
        [],
        {},
    )
    REPORTING = (
        "reporting",
        "Generating reports and visualizations for analysis",
        STRATEGY_SELECTION,
        [],
        {},
    )
    DEPLOYMENT = (
        "deployment",
        "Deploying the selected strategy for live trading",
        REPORTING,
        [],
        {},
    )

    def __init__(self, value, description, required_columns, rename_map):
        self._value_ = value
        self.description = description
        self.incoming_stage = None
        self.required_columns = required_columns
        self.rename_map = rename_map
