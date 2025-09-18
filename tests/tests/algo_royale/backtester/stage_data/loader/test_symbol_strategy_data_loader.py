from unittest.mock import MagicMock
import pytest
from datetime import datetime

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import SymbolStrategyDataLoader
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.stage_data.loader.mock_stage_data_loader import MockStageDataLoader
from tests.mocks.mock_loggable import MockLoggable

logger = MockLoggable()


@pytest.fixture
def loader():
    """Fixture for a SymbolStrategyDataLoader instance with mocked dependencies."""
    loader = SymbolStrategyDataLoader(
        stage_data_manager=MockStageDataManager(
            data_dir=MagicMock(),
        ),
        stage_data_loader=MockStageDataLoader(),
        logger=MockLoggable(),
    )
    # Patch write_error_file to do nothing
    loader.stage_data_manager.write_error_file = lambda *args, **kwargs: None
    yield loader


def set_stage_data_loader_raise_exception(
    loader: SymbolStrategyDataLoader, value: bool
):
    loader.stage_data_loader.set_raise_exception(value)


def reset_stage_data_loader(loader: SymbolStrategyDataLoader):
    loader.stage_data_manager.reset()
    loader.stage_data_loader.reset()
    loader.stage_data_manager.write_error_file = lambda *args, **kwargs: None


@pytest.mark.asyncio
class TestSymbolStrategyDataLoader:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, loader: SymbolStrategyDataLoader):
        reset_stage_data_loader(loader)
        yield
        reset_stage_data_loader(loader)

    async def test_load_data_normal(self, loader: SymbolStrategyDataLoader):
        # Should return a dict (mocked)
        result = await loader.load_data(
            stage=BacktestStage.DATA_INGEST,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 2),
            strategy_name="test_strategy",
            reverse_pages=False,
        )
        assert isinstance(result, dict)

    async def test_load_data_exception(self, loader: SymbolStrategyDataLoader):
        set_stage_data_loader_raise_exception(loader, True)
        result = await loader.load_data(
            stage=BacktestStage.DATA_INGEST,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 2),
            strategy_name="test_strategy",
            reverse_pages=False,
        )
        assert result == {}
        set_stage_data_loader_raise_exception(loader, False)

    def test_get_watchlist(self, loader: SymbolStrategyDataLoader):
        watchlist = loader.get_watchlist()
        assert isinstance(watchlist, list)