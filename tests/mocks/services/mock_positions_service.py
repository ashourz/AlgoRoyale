from algo_royale.services.positions_service import PositionsService
from tests.mocks.adapters.mock_positions_adapter import MockPositionsAdapter
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_trade_repo import MockTradeRepo


class MockPositionsService(PositionsService):
    def __init__(self):
        super().__init__(
            positions_adapter=MockPositionsAdapter(),
            trade_repo=MockTradeRepo(),
            logger=MockLoggable(),
            user_id="user_1",
            account_id="account_1",
        )

    def set_return_empty(self, value: bool):
        self.positions_adapter.set_return_empty(value)
        self.trade_repo.set_return_empty(value)

    def reset_return_empty(self):
        self.positions_adapter.reset_return_empty()
        self.trade_repo.reset_return_empty()

    def set_raise_exception(self, value: bool):
        self.positions_adapter.set_raise_exception(value)
        self.trade_repo.set_raise_exception(value)

    def reset_raise_exception(self):
        self.positions_adapter.reset_raise_exception()
        self.trade_repo.reset_raise_exception()

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
