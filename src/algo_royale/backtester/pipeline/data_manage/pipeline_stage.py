from enum import Enum

class PipelineStage(str, Enum):
    """Enum representing different stages of the data pipeline.
    Each stage corresponds to a specific task in the data processing workflow.
    The stages are:
    - DATA_INGEST: Loading and staging raw/unprocessed data (from API, files, DB, etc.)
    - DATA_CLEANING: Cleaning and preprocessing data (removing duplicates, filling missing values, etc.)
    - FEATURE_ENGINEERING: Creating new features from existing data (technical indicators, etc.)
    - BACKTEST: Backtesting strategies on historical data
    - STRATEGY_OPTIMIZATION: Optimizing strategies using historical data
    - RESULTS_ANALYSIS: Analyzing backtest results and performance metrics
    - STRATEGY_METRICS: Calculating and reporting strategy performance metrics
    - STRATEGY_SELECTION: Selecting the best strategy based on performance metrics
    - REPORTING: Generating reports and visualizations for analysis
    - DEPLOYMENT: Deploying the selected strategy for live trading
    """
    DATA_INGEST = "data_ingest" #Loading and staging raw/unprocessed data (from API, files, DB, etc.)
    DATA_CLEANING = "data_cleaning" #Cleaning and preprocessing data (removing duplicates, filling missing values, etc.)
    FEATURE_ENGINEERING = "feature_engineering" #Creating new features from existing data (technical indicators, etc.)
    BACKTEST = "backtest" #Backtesting strategies on historical data
    STRATEGY_OPTIMIZATION = "strategy_optimization" #Optimizing strategies using historical data
    RESULTS_ANALYSIS = "results_analysis" #Analyzing backtest results and performance metrics
    STRATEGY_METRICS = "strategy_metrics" #Calculating and reporting strategy performance metrics
    STRATEGY_SELECTION = "strategy_selection" #Selecting the best strategy based on performance metrics
    REPORTING = "reporting" #Generating reports and visualizations for analysis
    DEPLOYMENT = "deployment" #Deploying the selected strategy for live trading
    
    
class StageMarker(str, Enum):
    """Markers for directory status at each pipeline stage."""
    INGESTED = ".ingested"
    PREPARED = ".prepared"
    BACKTESTED = ".backtested"
    OPTIMIZED = ".optimized"
    SELECTED = ".selected"
    DEPLOYED = ".deployed"
    DONE = ".done"
    # Error markers for each stage
    ERROR_INGEST = ".error.ingest"
    ERROR_PREPARE = ".error.prepare"
    ERROR_BACKTEST = ".error.backtest"
    ERROR_OPTIMIZE = ".error.optimize"
    ERROR_SELECT = ".error.select"
    ERROR_DEPLOY = ".error.deploy"
    ERROR_UNKNOWN = ".error.unknown"

class DataFileExtension(str, Enum):
    """Extensions for files at each pipeline stage."""
    RAW = ".raw.csv"
    CLEANED = ".cleaned.csv"
    BACKTEST = ".backtest.csv"
    OPTIMIZED = ".optimized.csv"
    FINAL = ".final.csv"
    # Error markers for files
    ERROR_CORRUPT = ".error.corrupt"
    ERROR_MISSING = ".error.missing"
    ERROR_FORMAT = ".error.format"