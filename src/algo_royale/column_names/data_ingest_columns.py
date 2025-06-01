from algo_royale.column_names.base_column_names import BaseColumnNames
from algo_royale.column_names.column_name import ColumnName


class DataIngestColumns(BaseColumnNames):
    """Column names used during data ingestion and initial processing."""

    RAW_EXCHANGE = ColumnName("exchange")
    TIMESTAMP = ColumnName("timestamp")
    OPEN_PRICE = ColumnName("open_price")
    HIGH_PRICE = ColumnName("high_price")
    LOW_PRICE = ColumnName("low_price")
    CLOSE_PRICE = ColumnName("close_price")
    VOLUME = ColumnName("volume")
    NUM_TRADES = ColumnName("num_trades")
    VOLUME_WEIGHTED_PRICE = ColumnName("volume_weighted_price")
