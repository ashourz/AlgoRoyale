from enum import Enum

class PipelineStage(str, Enum):
    DATA_INGEST = "data_ingest"
    BACKTEST = "backtest"
    RESULTS_ANALYSIS = "results_analysis"
    STRATEGY_METRICS = "strategy_metrics"
    STRATEGY_SELECTION = "strategy_selection"
    REPORTING = "reporting"
    
class DataExtension(str, Enum):
    UNPROCESSED = ".unprocessed"
    PROCESSING = ".processing"
    PROCESSED = ".processed"
    DONE = ".done"