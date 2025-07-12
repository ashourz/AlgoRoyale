import asyncio
from algo_royale.logging.loggable import Loggable

import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import (
    SignalStrategyColumns,
    SignalStrategyExecutorColumns,
)


def validate_async_iterator_dict(
    data: dict, required_columns: list[str], logger: Loggable
) -> bool:
    """
    Validate that the input is a dictionary where each value is a callable that returns an async iterator
    yielding pandas DataFrames with the required columns."""
    if not isinstance(data, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {data}")
        return False
    for symbol, factory in data.items():
        if not isinstance(symbol, str):
            logger.warning(f"Validation failed: Symbol not str. Value: {symbol}")
            return False
        if not callable(factory):
            logger.warning(
                f"Validation failed: Factory not callable. Symbol: {symbol}, Value: {factory}"
            )
            return False
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
                logger.warning(
                    f"Validation failed: Page not DataFrame. Symbol: {symbol}, Value: {page_df}"
                )
                return False
            for col in required_columns:
                if col not in page_df.columns:
                    logger.warning(
                        f"Validation failed: Required column missing. Symbol: {symbol}, Column: {col}, Columns: {page_df.columns}"
                    )
                    return False
        except Exception as e:
            logger.warning(
                f"Validation failed: Exception during async iteration. Symbol: {symbol}, Exception: {e}"
            )
            return False
    return True


def validate_iterator_dict(
    output: dict[str, pd.DataFrame], required_columns: list[str], logger: Loggable
) -> bool:
    """
    Validate the output of SignalStrategyBacktestExecutor.
    Each DataFrame must contain the required columns.
    """
    if not isinstance(output, dict):
        logger.warning(f"Validation failed: Not a dict. Value: {output}")
        return False
    for symbol, df_list in output.items():
        if not isinstance(symbol, str):
            logger.warning(f"Validation failed: Symbol not str. Value: {symbol}")
            return False
        if not isinstance(df_list, list):
            logger.warning(
                f"Validation failed: df_list not a list. Symbol: {symbol}, Value: {df_list}"
            )
            return False
        for df in df_list:
            if not isinstance(df, pd.DataFrame):
                logger.warning(
                    f"Validation failed: Item in df_list not a DataFrame. Symbol: {symbol}, Value: {df}"
                )
                return False
            for col in required_columns:
                if col not in df.columns:
                    logger.warning(
                        f"Validation failed: Required column missing. Symbol: {symbol}, Column: {col}, Columns: {df.columns}"
                    )
                    return False
    return True


def validate_signal_strategy_backtest_executor_input(
    data: dict[str, callable], logger: Loggable
) -> bool:
    """
    Validate input for SignalStrategyBacktestExecutor.
    Each value must be a callable returning an async iterator yielding DataFrames with required columns.
    """
    return validate_async_iterator_dict(
        data, SignalStrategyColumns.get_all_column_values(), logger
    )


def validate_signal_strategy_backtest_executor_output(
    output: dict[str, pd.DataFrame], logger: Loggable
) -> bool:
    """
    Validate the output of SignalStrategyBacktestExecutor.
    Each DataFrame must contain the required columns.
    """
    return validate_iterator_dict(
        output, SignalStrategyExecutorColumns.get_all_column_values(), logger
    )
