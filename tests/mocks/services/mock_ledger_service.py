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

    def set_raise_exception(self, value: bool):
        self.cash_service.set_raise_exception(value)
        self.position_service.set_raise_exception(value)
        self.order_service.set_raise_exception(value)
        self.trades_service.set_raise_exception(value)
        self.enriched_data_service.set_raise_exception(value)

    def reset_raise_exception(self):
        self.cash_service.reset_raise_exception()
        self.position_service.reset_raise_exception()
        self.order_service.reset_raise_exception()
        self.trades_service.reset_raise_exception()
        self.enriched_data_service.reset_raise_exception()

    def set_return_empty(self, value: bool):
        self.position_service.set_return_empty(value)
        self.order_service.set_return_empty(value)
        self.trades_service.set_return_empty(value)
        self.enriched_data_service.set_return_empty(value)

    def reset_return_empty(self):
        self.position_service.reset_return_empty()
        self.order_service.reset_return_empty()
        self.trades_service.reset_return_empty()
        self.enriched_data_service.reset_return_empty()

    def reset(self):
        self.cash_service.reset()
        self.position_service.reset()
        self.order_service.reset()
        self.trades_service.reset()
        self.enriched_data_service.reset()
        self.entries = []
        self.sod_cash = 100000.0  # Reset to default start of day cash
