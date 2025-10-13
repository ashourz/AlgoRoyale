import pytest

from algo_royale.backtester.stage_data.writer.symbol_strategy_data_writer import (
    SymbolStrategyDataWriter,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.stage_data.writer.mock_stage_data_writer import (
    MockStageDataWriter,
)
from tests.mocks.mock_loggable import MockLoggable

logger = MockLoggable()


@pytest.fixture
def writer():
    """Fixture for a SymbolStrategyDataWriter instance with mocked dependencies."""
    writer = SymbolStrategyDataWriter(
        stage_data_manager=MockStageDataManager(),
        data_writer=MockStageDataWriter(),
        logger=MockLoggable(),
    )
    yield writer


def set_stage_data_loader_raise_exception(
    writer: SymbolStrategyDataWriter, value: bool
):
    writer.data_writer.set_raise_exception(value)


def reset_stage_data_loader(writer: SymbolStrategyDataWriter):
    writer.stage_data_manager.reset()
    writer.data_writer.reset()


@pytest.mark.asyncio
class TestSymbolStrategyDataWriter:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, writer: SymbolStrategyDataWriter):
        reset_stage_data_loader(writer)
        yield
        reset_stage_data_loader(writer)

    async def test_write_symbol_strategy_data_factory(
        self, writer: SymbolStrategyDataWriter
    ):
        result = await writer.async_write_symbol_strategy_data_factory(
            stage="stage1",
            symbol_strategy_data_factory=dict(),
            start_date=None,
            end_date=None,
        )
        assert result is None

    async def test_write_symbol_strategy_data_factory_with_exception(
        self, writer: SymbolStrategyDataWriter
    ):
        set_stage_data_loader_raise_exception(writer, True)
        result = await writer.async_write_symbol_strategy_data_factory(
            stage="stage1",
            symbol_strategy_data_factory=dict(),
            start_date=None,
            end_date=None,
        )
        assert result is None
