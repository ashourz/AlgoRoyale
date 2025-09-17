from algo_royale.models.alpaca_trading.alpaca_position import Position
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
        self.return_empty = False
        self.raise_exception = False
        self.mock_positions: list[Position] = [
            Position(
                asset_id="asset_id_1",
                symbol="AAPL",
                exchange="NASDAQ",
                asset_class="us_equity",
                asset_marginable=True,
                qty=10,
                qty_available=10,
                avg_entry_price=150.0,
                side="long",
                market_value=1550.0,
                cost_basis=1500.0,
                unrealized_pl=50.0,
                unrealized_plpc=0.0333,
                unrealized_intraday_pl=5.0,
                unrealized_intraday_plpc=0.003,
                current_price=155.0,
                lastday_price=153.0,
                change_today=0.02,
            ),
            Position(
                asset_id="asset_id_2",
                symbol="TSLA",
                exchange="NASDAQ",
                asset_class="us_equity",
                asset_marginable=True,
                qty=5,
                qty_available=5,
                avg_entry_price=700.0,
                side="short",
                market_value=3475.0,
                cost_basis=3500.0,
                unrealized_pl=-25.0,
                unrealized_plpc=-0.0071,
                unrealized_intraday_pl=-10.0,
                unrealized_intraday_plpc=-0.002,
                current_price=695.0,
                lastday_price=700.0,
                change_today=-0.015,
            ),
        ]
        self.positions = self.mock_positions.copy()

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
        self.positions = self.mock_positions.copy()

    def get_positions(self):
        if self.raise_exception:
            raise ValueError("Mock exception in get_positions")
        if self.return_empty:
            return []
        return self.positions

    def get_positions_by_symbol(self, symbol: str):
        if self.raise_exception:
            raise ValueError("Mock exception in get_positions_by_symbol")
        if self.return_empty:
            return []
        return [pos for pos in self.positions if pos.symbol == symbol]

    def get_positions_by_status(self, status: str):
        if self.raise_exception:
            raise ValueError("Mock exception in get_positions_by_status")
        if self.return_empty:
            return []
        # For simplicity, assume 'open' returns all positions
        if status == "open":
            return self.positions
        return []  # No other statuses handled in mock

    async def sync_positions(self):
        if self.raise_exception:
            raise ValueError("Mock exception in sync_positions")
        if self.return_empty:
            self.positions = []
        else:
            self.positions = self.mock_positions.copy()
        return None

    async def validate_positions(self):
        return None
