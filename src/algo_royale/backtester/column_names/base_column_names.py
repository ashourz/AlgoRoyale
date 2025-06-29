from algo_royale.backtester.column_names.column_name import ColumnName


class BaseColumnNames:
    """Base class for defining column names used in the algorithmic trading framework.

    Attributes:
        CLOSE (str): Column name for closing prices.
        OPEN (str): Column name for opening prices.
        HIGH (str): Column name for high prices.
        LOW (str): Column name for low prices.
        VOLUME (str): Column name for trading volume.
        DATETIME (str): Column name for datetime values.
        SYMBOL (str): Column name for stock or asset symbols.
    """

    ##TODO: confirm base classes from data

    VOLUME = ColumnName("volume")
    SYMBOL = ColumnName("symbol")
