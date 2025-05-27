from unittest.mock import MagicMock

import pytest

from algo_royale.backtester.data_stream.normalized_data_stream import (
    NormalizedDataStream,
)
from algo_royale.backtester.data_stream.normalized_data_stream_factory import (
    NormalizedDataStreamFactory,
)


class DummyStage:
    pass


@pytest.fixture
def data_preparer():
    return MagicMock()


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def factory(data_preparer, logger):
    return NormalizedDataStreamFactory(data_preparer, logger)


def test_create_returns_normalized_data_stream(factory, data_preparer, logger):
    symbol = "AAPL"
    iterator_factory = MagicMock()
    stage = DummyStage()
    stream = factory.create(symbol, iterator_factory, stage)
    assert isinstance(stream, NormalizedDataStream)
    assert stream.symbol == symbol
    assert stream.iterator_factory == iterator_factory
    assert stream.stage == stage
    assert stream.data_preparer == data_preparer
    assert stream.logger == logger
