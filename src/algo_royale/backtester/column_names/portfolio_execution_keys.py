class BaseKeyNames:
    """Base class for defining key names used in output/result dictionaries."""

    @classmethod
    def _get_all_key_objects(cls) -> list:
        """
        Returns a list of all key objects defined in a BaseKeyNames subclass.
        """
        return [
            getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith("__") and not callable(getattr(cls, attr))
        ]

    @classmethod
    def get_all_key_values(cls) -> list[str]:
        """
        Returns a list of string values from a BaseKeyNames subclass.
        """
        return [str(key) for key in cls._get_all_key_objects()]


class PortfolioExecutionKeys(BaseKeyNames):
    """Keys used in the output dictionary from portfolio execution."""

    PORTFOLIO_VALUES = "portfolio_values"
    CASH_HISTORY = "cash_history"
    HOLDINGS_HISTORY = "holdings_history"
    FINAL_CASH = "final_cash"
    FINAL_HOLDINGS = "final_holdings"
    TRANSACTIONS = "transactions"
    TRANSACTIONS_DF = "transactions_df"
    PORTFOLIO_VALUES_DF = "portfolio_values_df"
    METRICS = "metrics"
    EMPTY_RESULT = "empty_result"
    INVALID_OUTPUT = "invalid_output"


class PortfolioExecutionMetricsKeys(BaseKeyNames):
    """Keys used in the 'metrics' dictionary in portfolio execution output."""

    TOTAL_RETURN = "total_return"
    PORTFOLIO_RETURNS = "portfolio_returns"
    ERROR = "error"
