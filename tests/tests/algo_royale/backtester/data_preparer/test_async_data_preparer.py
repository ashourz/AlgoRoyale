from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer


class DummyStage:
    rename_map = {"old": "new", "foo": "bar"}
    required_input_columns = ["new", "bar"]


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def preparer(logger):
    return AsyncDataPreparer(logger)


@pytest.mark.asyncio
async def test_normalized_stream_yields_normalized(preparer):
    async def async_gen():
        yield pd.DataFrame({"old": [1], "foo": [2]})
        yield pd.DataFrame({"old": [3], "foo": [4]})

    results = []
    async for df in preparer.normalized_stream(
        DummyStage(), "AAPL", lambda: async_gen()
    ):
        results.append(df)
    assert len(results) == 2
    assert list(results[0].columns) == ["new", "bar"]


@pytest.mark.asyncio
async def test_normalized_stream_handles_exception(preparer, logger):
    async def async_gen():
        yield pd.DataFrame({"old": [1], "foo": [2]})
        yield pd.DataFrame({"bad": [2]})  # Will cause normalize_dataframe to fail

    results = []
    async for df in preparer.normalized_stream(
        DummyStage(), "AAPL", lambda: async_gen()
    ):
        results.append(df)
    # Only the first should yield, and it should have the renamed columns
    assert len(results) == 1
    assert list(results[0].columns) == ["new", "bar"]
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
    async for _ in preparer.normalized_stream(DummyStage(), "AAPL", lambda: iterator):
        pass
    assert closed
