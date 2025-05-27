from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer


class DummyStage:
    rename_map = {"old": "new"}
    required_columns = ["new"]


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def preparer(logger):
    return AsyncDataPreparer(logger)


@pytest.mark.asyncio
async def test_normalized_stream_yields_normalized(preparer):
    # Async generator yielding two DataFrames
    async def async_gen():
        yield pd.DataFrame({"old": [1]})
        yield pd.DataFrame({"old": [2]})

    # Use DummyStage as config
    results = []
    async for df in preparer.normalized_stream(
        "AAPL", lambda: async_gen(), DummyStage()
    ):
        results.append(df)
    assert len(results) == 2
    assert list(results[0].columns) == ["new"]


@pytest.mark.asyncio
async def test_normalized_stream_handles_exception(preparer, logger):
    # Async generator yields one good, one bad DataFrame
    async def async_gen():
        yield pd.DataFrame({"old": [1]})
        yield pd.DataFrame({"bad": [2]})  # Will cause normalize_dataframe to fail

    results = []
    async for df in preparer.normalized_stream(
        "AAPL", lambda: async_gen(), DummyStage()
    ):
        results.append(df)
    assert len(results) == 1  # Only the first yields
    logger.error.assert_called()


@pytest.mark.asyncio
async def test_normalized_stream_aclose_called(preparer):
    closed = False

    class Iterator:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

        async def aclose(self):
            nonlocal closed
            closed = True

    iterator = Iterator()
    async for _ in preparer.normalized_stream("AAPL", lambda: iterator, DummyStage()):
        pass
    assert closed
