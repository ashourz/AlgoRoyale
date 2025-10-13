from unittest.mock import AsyncMock, MagicMock

import pytest

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_watchlist_repo import MockWatchlistRepo

logger = MockLoggable()


@pytest.fixture
def stage_data_loader():
    """Fixture for a StageDataLoader instance with mocked dependencies."""
    loader = StageDataLoader(
        logger=MockLoggable(),
        stage_data_manager=MockStageDataManager(),
        watchlist_repo=MockWatchlistRepo(),
    )
    yield loader


def reset_stage_data_loader(loader: StageDataLoader):
    loader.stage_data_manager.reset()
    loader.watchlist_repo.reset()


class TestStageDataLoader:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, stage_data_loader: StageDataLoader):
        reset_stage_data_loader(stage_data_loader)
        yield
        reset_stage_data_loader(stage_data_loader)

    def test_get_watchlist(self, stage_data_loader):
        # Should return the mock watchlist
        watchlist = stage_data_loader.get_watchlist()
        assert isinstance(watchlist, list)

    @pytest.mark.asyncio
    async def test_load_all_stage_data_normal(self, stage_data_loader):
        # Patch dependencies
        stage_data_loader._get_all_existing_data_symbols = AsyncMock(
            return_value=["AAPL", "GOOG"]
        )
        stage_data_loader.get_watchlist = MagicMock(return_value=["AAPL", "GOOG"])
        stage_data_loader.load_stage_data = MagicMock(return_value=lambda: AsyncMock())

        result = await stage_data_loader.load_all_stage_data(BacktestStage.DATA_INGEST)
        assert "AAPL" in result and "GOOG" in result
        assert callable(result["AAPL"])
        assert callable(result["GOOG"])

    @pytest.mark.asyncio
    async def test_load_all_stage_data_no_symbols(self, stage_data_loader):
        stage_data_loader._get_all_existing_data_symbols = AsyncMock(return_value=[])
        stage_data_loader.get_watchlist = MagicMock(return_value=[])
        result = await stage_data_loader.load_all_stage_data(BacktestStage.DATA_INGEST)
        assert result == {}

    def test_load_stage_data_returns_callable(self, stage_data_loader):
        # Should return a callable that is an async generator
        gen_callable = stage_data_loader.load_stage_data(
            symbol="AAPL",
            stage=BacktestStage.DATA_INGEST,
            start_date=None,
            end_date=None,
        )
        assert callable(gen_callable)
        # The returned callable should be an async generator when called
        gen = gen_callable()
        assert hasattr(gen, "__aiter__")

    @pytest.mark.asyncio
    async def test_load_symbol_no_data(self, stage_data_loader):
        # Patch _get_stage_symbol_dir and _has_existing_data to simulate missing data
        stage_data_loader._get_stage_symbol_dir = MagicMock(return_value=MagicMock())
        stage_data_loader._has_existing_data = MagicMock(return_value=False)
        with pytest.raises(ValueError):
            async for _ in stage_data_loader.load_symbol(
                BacktestStage.DATA_INGEST, "AAPL"
            ):
                pass

    @pytest.mark.asyncio
    async def test_load_symbol_with_data(self, stage_data_loader):
        # Patch _get_stage_symbol_dir and _has_existing_data to simulate data exists
        stage_data_loader._get_stage_symbol_dir = MagicMock(return_value=MagicMock())
        stage_data_loader._has_existing_data = MagicMock(return_value=True)

        async def async_gen(**kwargs):
            yield MagicMock()

        stage_data_loader._stream_existing_data_async = async_gen

        result = []
        async for df in stage_data_loader.load_symbol(
            BacktestStage.DATA_INGEST, "AAPL"
        ):
            result.append(df)
        assert result  # Should yield at least one DataFrame

    @pytest.mark.asyncio
    async def test__get_all_existing_data_symbols(self, stage_data_loader):
        # Patch get_watchlist and dependencies to simulate various symbol states
        stage_data_loader.get_watchlist = MagicMock(
            return_value=["AAPL", "GOOG", "MSFT"]
        )
        stage_data_loader._get_stage_symbol_dir = MagicMock(return_value=MagicMock())
        stage_data_loader._has_existing_data = MagicMock(
            side_effect=[True, False, True]
        )
        stage_data_loader.stage_data_manager.is_symbol_stage_done = MagicMock(
            side_effect=[True, True, False]
        )
        stage_data_loader.stage_data_manager.write_error_file = MagicMock()

        done = await stage_data_loader._get_all_existing_data_symbols(
            stage=BacktestStage.DATA_INGEST, strategy_name="test_strategy"
        )
        # Only AAPL and MSFT should be done (GOOG missing)
        assert done == ["AAPL", "MSFT"]

    def test__get_stage_symbol_dir(self, stage_data_loader):
        # Should delegate to stage_data_manager.get_directory_path
        stage_data_loader.stage_data_manager.get_directory_path = MagicMock(
            return_value="mock_path"
        )
        result = stage_data_loader._get_stage_symbol_dir(
            stage=BacktestStage.DATA_INGEST, symbol="AAPL"
        )
        assert result == "mock_path"

    def test__has_existing_data(self, stage_data_loader):
        # Should return False if path does not exist
        fake_path = MagicMock()
        fake_path.exists.return_value = False
        assert not stage_data_loader._has_existing_data(fake_path)
        # Should return True if path exists and has files
        fake_path.exists.return_value = True
        fake_path.iterdir.return_value = [MagicMock()]
        assert stage_data_loader._has_existing_data(fake_path)
        # Should return False if path exists but is empty
        fake_path.iterdir.return_value = []
        assert not stage_data_loader._has_existing_data(fake_path)
