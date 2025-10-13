from enum import Enum

class DataExtension(str, Enum):
    """Enum representing different data file extensions used in the pipeline.
    Each extension corresponds to a specific stage or status of the data processing workflow.
    The extensions are:
    - UNPROCESSED: Raw ingest, not staged/cleaned yet
    - PROCESSING: In progress, not yet finished
    - PROCESSED: Staged and cleaned, ready for analysis
    - DONE: Finished, all steps completed
    - INCOMPLETE: Incomplete, not all steps completed
    - ERROR: Error occurred during processing
    """
    UNPROCESSED = "unprocessed"   # Raw ingest, not staged/cleaned yet
    PROCESSING = "processing"     # In progress, not yet finished
    PROCESSED = "processed"       # Staged and cleaned, ready for analysis
    DONE = "done"                 # Finished, all steps completed
    INCOMPLETE = "incomplete"     # Incomplete, not all steps completed
    ERROR = "error" 