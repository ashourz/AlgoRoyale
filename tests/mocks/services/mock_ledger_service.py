from decimal import Decimal
from uuid import UUID

from algo_royale.models.db.db_order import DBOrder
from algo_royale.services.ledger_service import LedgerService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_account_cash_service import MockAccountCashService
from tests.mocks.services.mock_enriched_data_service import MockEnrichedDataService
from tests.mocks.services.mock_order_service import MockOrderService
from tests.mocks.services.mock_positions_service import MockPositionsService
from tests.mocks.services.mock_trades_service import MockTradesService


class MockLedgerService(LedgerService):
    def __init__(self):
        self.cash_service = MockAccountCashService()
        self.order_service = MockOrderService()
        self.trades_service = MockTradesService()
        self.position_service = MockPositionsService()
        self.enriched_data_service = MockEnrichedDataService()
        self.logger = MockLoggable()
        super().__init__(
            cash_service=self.cash_service,
            order_service=self.order_service,
            trades_service=self.trades_service,
            position_service=self.position_service,
            enriched_data_service=self.enriched_data_service,
            logger=self.logger,
        )
        self.entries = []
        self.sod_cash = 100000.0  # Default start of day cash for testing
        self.raise_exception = False
        self.return_empty = False
        from datetime import datetime

        self.mock_order = DBOrder(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id="user_123",
            account_id="account_123",
            symbol="AAPL",
            market="NASDAQ",
            order_type="market",
            action="buy",
            settled=True,
            notional=100.0,
            quantity=1,
            price=100.0,
            status="filled",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            qty=1,
            filled_qty=1,
            type="market",
            side="buy",
            time_in_force="day",
            submitted_at=None,
            filled_at=None,
            expired_at=None,
            canceled_at=None,
            failed_at=None,
            replaced_at=None,
            client_order_id="client_123",
            order_class=None,
            take_profit=None,
            stop_loss=None,
            trail_price=None,
            trail_percent=None,
        )

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.reset_raise_exception()
        self.reset_return_empty()
        self.entries = []
        self.sod_cash = 100000.0  # Reset to default start of day cash

    def get_current_position(self, symbol) -> int:
        if self.raise_exception:
            return 0
        if self.return_empty:
            return 0
        return 1

    def get_available_cash(self) -> float:
        if self.raise_exception:
            return 0.0
        if self.return_empty:
            return 0.0
        return 50000.0  # Mock available cash for testing

    def init_sod_cash(self, amount: float) -> None:
        if self.raise_exception:
            raise Exception("Mock exception in init_sod_cash")

    def calculate_weighted_notional(self, symbol: str, weight: float) -> Decimal:
        if self.raise_exception:
            return Decimal(0)
        if self.return_empty:
            return Decimal(0)
        return Decimal(10000.0)  # Mock weighted notional for testing

    def fetch_order_by_id(self, order_id) -> DBOrder | None:
        if self.raise_exception:
            return None
        if self.return_empty:
            return None
        return self.mock_order.model_copy(update={"id": order_id})

    def submit_equity_order(self, order, enriched_data) -> None:
        return None

    def update_order(
        self,
        order_id: str,
        status: str,
        quantity: int | None = None,
        price: float | None = None,
        filled_qty: int | None = None,
    ) -> None:
        return None
