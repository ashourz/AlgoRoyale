from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.data_stream.normalized_data_stream import (
    NormalizedDataStream,
)


class DummyStage:
    rename_map = {"old": "new"}
    required_columns = ["new"]


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def data_preparer(logger):
    from algo_royale.backtester.data_preparer.data_preparer import DataPreparer

    return DataPreparer(logger)


@pytest.mark.asyncio
async def test_normalized_data_stream_yields_normalized(data_preparer, logger):
    # Async generator yielding two DataFrames
    async def async_gen():
        yield pd.DataFrame({"old": [1]})
        yield pd.DataFrame({"old": [2]})

    stream = NormalizedDataStream(
        symbol="AAPL",
        iterator_factory=lambda: async_gen(),
        stage=DummyStage(),
        data_preparer=data_preparer,
        logger=logger,
    )
    results = []
    async for df in stream:
        results.append(df)
    assert len(results) == 2
    assert list(results[0].columns) == ["new"]


@pytest.mark.asyncio
async def test_normalized_data_stream_handles_exception(data_preparer, logger):
    # Async generator yields one good, one bad DataFrame
    async def async_gen():
        yield pd.DataFrame({"old": [1]})
        yield pd.DataFrame({"bad": [2]})  # Will cause normalize_dataframe to fail

    stream = NormalizedDataStream(
        symbol="AAPL",
        iterator_factory=lambda: async_gen(),
        stage=DummyStage(),
        data_preparer=data_preparer,
        logger=logger,
    )
    results = []
    async for df in stream:
        results.append(df)
    assert len(results) == 1  # Only the first yields
    logger.error.assert_called()


@pytest.mark.asyncio
async def test_normalized_data_stream_aclose_called(data_preparer, logger):
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
    stream = NormalizedDataStream(
        symbol="AAPL",
        iterator_factory=lambda: iterator,
        stage=DummyStage(),
        data_preparer=data_preparer,
        logger=logger,
    )
    async for _ in stream:
        pass
    assert closed
