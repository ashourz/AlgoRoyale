from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.column_names.strategy_columns import (
    SignalStrategyExecutorColumns,
)
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)


@pytest.fixture
def mock_stage_data_manager(tmp_path):
    mgr = MagicMock()
    mgr.get_directory_path.side_effect = lambda stage, strat, symbol: tmp_path
    mgr.is_symbol_stage_done.return_value = False
    # Create a dummy CSV file so glob("*.csv") is not empty
    (tmp_path / "dummy.csv").write_text("a,close_price,timestamp\n1,100,2020-01-01")
    return mgr


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_strategy():
    strat = MagicMock()
    strat.__class__.__name__ = "MockStrategy"
    strat.get_hash_id.return_value = "MockStrategy"  # <-- Add this line
    strat.generate_signals.side_effect = lambda df: pd.DataFrame(
        {
            SignalStrategyExecutorColumns.ENTRY_SIGNAL: ["buy"] * len(df),
            SignalStrategyExecutorColumns.EXIT_SIGNAL: ["hold"] * len(df),
        },
        index=df.index,
    )
    return strat


@pytest.mark.asyncio
async def test_run_backtest_success(
    mock_stage_data_manager, mock_logger, mock_strategy
):
    # Prepare async data iterator
    async def df_iter():
        yield pd.DataFrame(
            {
                "a": [1],
                SignalStrategyExecutorColumns.CLOSE_PRICE: [
                    100
                ],  # Changed from "close_price"
                SignalStrategyExecutorColumns.TIMESTAMP: pd.to_datetime(["2020-01-01"]),
            }
        )
        yield pd.DataFrame(
            {
                "a": [2],
                SignalStrategyExecutorColumns.CLOSE_PRICE: [
                    200
                ],  # Changed from "close_price"
                SignalStrategyExecutorColumns.TIMESTAMP: pd.to_datetime(["2020-01-02"]),
            }
        )

    data = {"AAPL": lambda: df_iter()}
    executor = StrategyBacktestExecutor(mock_stage_data_manager, mock_logger)
    results = await executor.run_backtest([mock_strategy], data)
    assert "AAPL" in results
    assert len(results["AAPL"]) == 2
    for df in results["AAPL"]:
        assert SignalStrategyExecutorColumns.ENTRY_SIGNAL in df.columns
        assert SignalStrategyExecutorColumns.EXIT_SIGNAL in df.columns
        assert SignalStrategyExecutorColumns.STRATEGY_NAME in df.columns
        assert SignalStrategyExecutorColumns.SYMBOL in df.columns


@pytest.mark.asyncio
async def test_run_backtest_empty_data(mock_stage_data_manager, mock_logger):
    executor = StrategyBacktestExecutor(mock_stage_data_manager, mock_logger)
    results = await executor.run_backtest([], {})
    assert results is None
    mock_logger.error.assert_called_with(
        "No data available - check your data paths and files"
    )


@pytest.mark.asyncio
async def test_run_backtest_skips_done(
    mock_stage_data_manager, mock_logger, mock_strategy
):
    # Mark stage as done for this symbol/strategy
    mock_stage_data_manager.is_symbol_stage_done.return_value = True

    async def df_iter():
        yield pd.DataFrame(
            {
                "a": [1],
                SignalStrategyExecutorColumns.CLOSE_PRICE: [100],
                SignalStrategyExecutorColumns.TIMESTAMP: pd.to_datetime(["2020-01-01"]),
            }
        )

    data = {"AAPL": lambda: df_iter()}
    executor = StrategyBacktestExecutor(mock_stage_data_manager, mock_logger)
    results = await executor.run_backtest([mock_strategy], data)
    # Should skip processing, so no results
    assert results == {}


@pytest.mark.asyncio
async def test_run_backtest_handles_page_exception(
    mock_stage_data_manager, mock_logger, mock_strategy
):
    # Strategy will raise on the second page
    def bad_generate_signals(df):
        if df["a"].iloc[0] == 2:
            raise ValueError("bad page")
        # Return a valid DataFrame for the first page
        return pd.DataFrame(
            {
                SignalStrategyExecutorColumns.ENTRY_SIGNAL: ["buy"] * len(df),
                SignalStrategyExecutorColumns.EXIT_SIGNAL: ["hold"] * len(df),
            },
            index=df.index,
        )

    mock_strategy.generate_signals.side_effect = bad_generate_signals

    async def df_iter():
        yield pd.DataFrame(
            {
                "a": [1],
                SignalStrategyExecutorColumns.CLOSE_PRICE: [100],
                SignalStrategyExecutorColumns.TIMESTAMP: pd.to_datetime(["2020-01-01"]),
            }
        )
        yield pd.DataFrame(
            {
                "a": [2],
                SignalStrategyExecutorColumns.CLOSE_PRICE: [200],
                SignalStrategyExecutorColumns.TIMESTAMP: pd.to_datetime(["2020-01-02"]),
            }
        )

    data = {"AAPL": lambda: df_iter()}
    executor = StrategyBacktestExecutor(mock_stage_data_manager, mock_logger)
    results = await executor.run_backtest([mock_strategy], data)
    # Only the first page should succeed
    assert len(results["AAPL"]) == 1
    mock_logger.error.assert_any_call(
        "Error processing page 2 for AAPL-MockStrategy: bad page"
    )
