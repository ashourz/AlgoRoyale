import asyncio

import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import (
    SignalStrategyColumns,
    SignalStrategyExecutorColumns,
)


def validate_async_iterator_dict(data: dict, required_columns: list[str]) -> bool:
    """
    Validate that the input is a dictionary where each value is a callable that returns an async iterator
    yielding pandas DataFrames with the required columns."""
    if not isinstance(data, dict):
        return False
    for symbol, factory in data.items():
        if not isinstance(symbol, str):
            return False
        if not callable(factory):
            return False
        # Try to get an async iterator and fetch one page
        try:

            async def get_first_page():
                async_iter = factory()
                page = None
                async for df in async_iter:
                    page = df
                    break
                return page

            page_df = asyncio.run(get_first_page())
            if not isinstance(page_df, pd.DataFrame):
                return False
            for col in required_columns:
                if col not in page_df.columns:
                    return False
        except Exception:
            return False
    return True


def validate_iterator_dict(
    output: dict[str, pd.DataFrame], required_columns: list[str]
) -> bool:
    """
    Validate the output of SignalStrategyBacktestExecutor.
    Each DataFrame must contain the required columns.
    """
    if not isinstance(output, dict):
        return False
    for symbol, df_list in output.items():
        if not isinstance(symbol, str):
            return False
        if not isinstance(df_list, list):
            return False
        for df in df_list:
            if not isinstance(df, pd.DataFrame):
                return False
            for col in required_columns:
                if col not in df.columns:
                    return False
    return True


def validate_signal_strategy_backtest_executor_input(data: dict[str, callable]) -> bool:
    """
    Validate input for SignalStrategyBacktestExecutor.
    Each value must be a callable returning an async iterator yielding DataFrames with required columns.
    """
    return validate_async_iterator_dict(
        data, SignalStrategyColumns.get_all_column_values()
    )


def validate_signal_strategy_backtest_executor_output(
    output: dict[str, pd.DataFrame],
) -> bool:
    """
    Validate the output of SignalStrategyBacktestExecutor.
    Each DataFrame must contain the required columns.
    """
    return validate_iterator_dict(
        output, SignalStrategyExecutorColumns.get_all_column_values()
    )
