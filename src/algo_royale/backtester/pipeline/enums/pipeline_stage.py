from enum import Enum

class PipelineStage(str, Enum):
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