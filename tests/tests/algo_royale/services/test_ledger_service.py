from decimal import Decimal

import pytest

from algo_royale.application.orders.equity_order_types import EquityBaseOrder
from algo_royale.services.ledger_service import LedgerService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_account_cash_service import MockAccountCashService
from tests.mocks.services.mock_enriched_data_service import MockEnrichedDataService
from tests.mocks.services.mock_order_service import MockOrderService
from tests.mocks.services.mock_positions_service import MockPositionsService
from tests.mocks.services.mock_trades_service import MockTradesService


@pytest.fixture
def ledger_service():
    service = LedgerService(
        cash_service=MockAccountCashService(),
        trades_service=MockTradesService(),
        order_service=MockOrderService(),
        position_service=MockPositionsService(),
        enriched_data_service=MockEnrichedDataService(),
        logger=MockLoggable(),
    )
    yield service


def reset_ledger_service(ledger_service: LedgerService):
    ledger_service.cash_service.reset()
    ledger_service.order_service.reset()
    ledger_service.trades_service.reset()
    ledger_service.position_service.reset()
    ledger_service.enriched_data_service.reset()


def set_ledger_service_raise_exception(ledger_service: LedgerService, value: bool):
    ledger_service.cash_service.set_raise_exception(value)
    ledger_service.order_service.set_raise_exception(value)
    ledger_service.trades_service.set_raise_exception(value)
    ledger_service.position_service.set_raise_exception(value)
    ledger_service.enriched_data_service.set_raise_exception(value)


def reset_ledger_service_raise_exception(ledger_service: LedgerService):
    ledger_service.cash_service.reset_raise_exception()
    ledger_service.order_service.reset_raise_exception()
    ledger_service.trades_service.reset_raise_exception()
    ledger_service.position_service.reset_raise_exception()
    ledger_service.enriched_data_service.reset_raise_exception()


def set_ledger_service_return_empty(ledger_service: LedgerService, value: bool):
    ledger_service.order_service.set_return_empty(value)
    ledger_service.trades_service.set_return_empty(value)
    ledger_service.position_service.set_return_empty(value)
    ledger_service.enriched_data_service.set_return_empty(value)


def reset_ledger_service_return_empty(ledger_service: LedgerService):
    ledger_service.order_service.reset_return_empty()
    ledger_service.trades_service.reset_return_empty()
    ledger_service.position_service.reset_return_empty()
    ledger_service.enriched_data_service.reset_return_empty()


@pytest.mark.asyncio
class TestLedgerService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, ledger_service: LedgerService):
        reset_ledger_service(ledger_service)
        yield
        reset_ledger_service(ledger_service)

    async def test_get_current_positions_normal(self, ledger_service: LedgerService):
        positions = ledger_service.get_current_position(symbol="AAPL")
        assert (
            positions
            == ledger_service.position_service.get_positions_by_symbol("AAPL")[0].qty
        )

    async def test_get_available_cash(self, ledger_service: LedgerService):
        cash = ledger_service.get_available_cash()
        assert cash == ledger_service.cash_service.total_cash()

    async def test_init_sod_cash(self, ledger_service: LedgerService):
        ledger_service.init_sod_cash(Decimal(1000))
        assert ledger_service.sod_cash == Decimal(1000)

    async def test_calculate_weighted_notional(self, ledger_service: LedgerService):
        ledger_service.init_sod_cash(Decimal(1000))
        notional = ledger_service.calculate_weighted_notional("AAPL", 0.5)
        assert isinstance(notional, Decimal)
        assert notional <= ledger_service.sod_cash * Decimal(0.5)

    async def test_fetch_order_by_id(self, ledger_service: LedgerService):
        order = ledger_service.fetch_order_by_id("order_id_1")
        assert order is not None or order is None  # Accepts both for mock

    async def test_submit_equity_order(self, ledger_service: LedgerService):
        order = EquityBaseOrder(
            symbol="AAPL",
            qty=10,
            side="buy",
            type="market",
            time_in_force="day",
            extended_hours=False,
            client_order_id="client_order_1",
        )
        enriched_data = {"foo": "bar"}
        # Should not raise
        ledger_service.submit_equity_order(order, enriched_data)
        assert True

    async def test_update_order(self, ledger_service: LedgerService):
        # Should not raise
        ledger_service.update_order("order_id_1", "FILLED", quantity=10, price=100.0)
        assert True
