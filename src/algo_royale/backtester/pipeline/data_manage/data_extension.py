from enum import Enum

class DataExtension(str, Enum):
    """Enum representing different data file extensions used in the pipeline.
    Each extension corresponds to a specific stage or status of the data processing workflow.
    The extensions are:
    - UNPROCESSED: Raw ingest, not staged/cleaned yet
    - PROCESSING: In progress, not yet finished
    - PROCESSED: Staged and cleaned, ready for analysis
    - BACKTESTED: Backtested, ready for optimization
    - OPTIMIZED: Optimized, ready for selection
    - SELECTED: Selected strategy, ready for deployment
    - DEPLOYED: Deployed strategy, live trading
    - DONE: Finished, all steps completed
    - INCOMPLETE: Incomplete, not all steps completed
    - ERROR: Error occurred during processing
    """
    UNPROCESSED = ".unprocessed" #Raw ingest, not staged/cleaned yet
    PROCESSING = ".processing" #In progress, not yet finished
    PROCESSED = ".processed" #Staged and cleaned, ready for analysis
    BACKTESTED = ".backtested" #Backtested, ready for optimization
    OPTIMIZED = ".optimized" #Optimized, ready for selection
    SELECTED = ".selected" #Selected strategy, ready for deployment
    DEPLOYED = ".deployed" #Deployed strategy, live trading
    DONE = ".done" #Finished, all steps completed
    INCOMPLETE = ".incomplete" #Incomplete, not all steps completed
    ERROR = ".error" #Error occurred during processing