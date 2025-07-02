from algo_royale.backtester.column_names.base_column_names import BaseColumnNames
from algo_royale.backtester.column_names.column_name import ColumnName


class PortfolioStrategyInputColumns(BaseColumnNames):
    """Column names used as input for portfolio strategies generate_signals method."""

    SIGNALS = ColumnName("signals")
    RETURNS = ColumnName("returns")


class PortfolioStrategyOutputColumns(BaseColumnNames):
    """Column names used as output for portfolio strategies generate_signals method."""

    PORTFOLIO_RETURNS = ColumnName("portfolio_returns")
