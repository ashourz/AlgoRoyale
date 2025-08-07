from pydantic import BaseModel


class SignalDataPayload(BaseModel):
    """SignalDataPayload is a Pydantic model that represents the payload for signal data.
    It includes fields for signals and price data, both of which are dictionaries.

        Attributes:
            signals (dict): A dictionary containing trading signals for various stock symbols.
                - SignalStrategyColumns.ENTRY_SIGNAL
                - SignalStrategyColumns.EXIT_SIGNAL
            price_data (dict): A dictionary containing price data for the corresponding stock symbols.
                - DataIngestColumns.PRICE
                - DataIngestColumns.TIMESTAMP
                - DataIngestColumns.OPEN_PRICE
                - DataIngestColumns.HIGH_PRICE
                - DataIngestColumns.LOW_PRICE
                - DataIngestColumns.CLOSE_PRICE
                - DataIngestColumns.VOLUME
                - DataIngestColumns.NUM_TRADES
                - DataIngestColumns.VOLUME_WEIGHTED_PRICE
    """

    signals: dict
    price_data: dict
