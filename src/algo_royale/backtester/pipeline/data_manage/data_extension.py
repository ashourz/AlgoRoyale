from enum import Enum

class DataExtension(str, Enum):
    UNPROCESSED = ".unprocessed" #Raw ingest, not staged/cleaned yet
    PROCESSING = ".processing" #In progress, not yet finished
    PROCESSED = ".processed" #Staged and cleaned, ready for analysis
    BACKTESTED = ".backtested" #Backtested, ready for optimization
    OPTIMIZED = ".optimized" #Optimized, ready for selection
    SELECTED = ".selected" #Selected strategy, ready for deployment
    DEPLOYED = ".deployed" #Deployed strategy, live trading
    DONE = ".done" #Finished, all steps completed
    ERROR = ".error" #Error occurred during processing