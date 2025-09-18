from unittest.mock import MagicMock

from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_watchlist_repo import MockWatchlistRepo


class MockStageDataLoader(StageDataLoader):
    def __init__(self):
        super().__init__(
            logger=MockLoggable(),
            stage_data_manager=MockStageDataManager(data_dir=MagicMock()),
            watchlist_repo=MockWatchlistRepo(),
        )
        self.base_watchlist = ["AAPL", "MSFT", "GOOGL"]
        self.raise_exception = False
        self.watchlist = self.base_watchlist

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def reset(self):
        self.raise_exception = False
        self.watchlist = self.base_watchlist

    def get_watchlist(self):
        return self.watchlist

    async def load_symbol(
        self,
        stage,
        symbol,
        strategy_name=None,
        reverse_pages=False,
        start_date=None,
        end_date=None,
    ):
        if self.raise_exception:
            raise Exception("Mocked exception")
        return super().load_symbol(
            stage, symbol, strategy_name, reverse_pages, start_date, end_date
        )

    async def load_all_stage_data(
        self,
        stage,
        strategy_name=None,
        start_date=None,
        end_date=None,
        reverse_pages=False,
    ):
        if self.raise_exception:
            raise Exception("Mocked exception")
        return await super().load_all_stage_data(
            stage, strategy_name, start_date, end_date, reverse_pages
        )

    def load_stage_data(
        self,
        symbol,
        stage,
        start_date,
        end_date,
        strategy_name=None,
        reverse_pages=True,
    ):
        if self.raise_exception:
            raise Exception("Mocked exception")
        return super().load_stage_data(
            symbol, stage, start_date, end_date, strategy_name, reverse_pages
        )
