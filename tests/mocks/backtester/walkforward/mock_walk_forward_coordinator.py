from unittest.mock import MagicMock

from algo_royale.backtester.walkforward.walk_forward_coordinator import (
    WalkForwardCoordinator,
)
from tests.mocks.mock_loggable import MockLoggable


class MockWalkForwardCoordinator(WalkForwardCoordinator):
    def __init__(self):
        super().__init__(
            stage_data_manager=MagicMock(),
            stage_data_loader=MagicMock(),
            data_ingest_stage_coordinator=MagicMock(),
            feature_engineering_stage_coordinator=MagicMock(),
            optimization_stage_coordinator=MagicMock(),
            testing_stage_coordinator=MagicMock(),
            logger=MockLoggable(),
        )
        self.run_async_called = False
        self.should_raise = False
        self.should_return_none = False
        self.return_value = {"mock": True}

    def set_raise(self, value: bool):
        self.should_raise = value

    def set_return_none(self, value: bool):
        self.should_return_none = value

    def set_return_value(self, value):
        self.return_value = value

    async def run_async(self):
        self.run_async_called = True
        if self.should_raise:
            raise RuntimeError("Mocked exception in run_async")
        if self.should_return_none:
            return None
        return self.return_value
