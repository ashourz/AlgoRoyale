from algo_royale.backtester.column_names.column_name import ColumnName
from algo_royale.backtester.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)


class StrategyColumns(FeatureEngineeringColumns):
    """Column names used in the strategy execution and management within the algorithmic trading framework."""

    TIMESTAMP = ColumnName("timestamp")
    STRATEGY_NAME = ColumnName("strategy_name")
    ENTRY_SIGNAL = ColumnName("entry_signal")
    EXIT_SIGNAL = ColumnName("exit_signal")
    TRAILING_STOP = ColumnName("trailing_stop")
