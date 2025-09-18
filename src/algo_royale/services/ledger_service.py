from decimal import Decimal

from algo_royale.application.orders.equity_order_types import EquityBaseOrder
from algo_royale.logging.loggable import Loggable
from algo_royale.models.db.db_order import DBOrder
from algo_royale.services.account_cash_service import AccountCashService
from algo_royale.services.enriched_data_service import EnrichedDataService
from algo_royale.services.orders_service import OrderService
from algo_royale.services.positions_service import PositionsService
from algo_royale.services.trades_service import TradesService


class LedgerService:
    def __init__(
        self,
        cash_service: AccountCashService,
        order_service: OrderService,
        trades_service: TradesService,
        position_service: PositionsService,
        enriched_data_service: EnrichedDataService,
        logger: Loggable,
    ):
        self.entries = []
        self.cash_service = cash_service
        self.order_service = order_service
        self.trades_service = trades_service
        self.position_service = position_service
        self.enriched_data_service = enriched_data_service
        self.logger = logger
        self.sod_cash = Decimal(0)

    def get_current_position(self, symbol: str) -> int:
        """Get the current position for a given symbol."""
        try:
            positions = self.position_service.get_positions_by_symbol(symbol)
            return sum(pos.qty for pos in positions)
        except Exception as e:
            self.logger.error(f"Error getting current position for {symbol}: {e}")
            return 0

    def get_available_cash(self) -> Decimal:
        """Get the available cash balance."""
        try:
            return self.cash_service.total_cash()
        except Exception as e:
            self.logger.error(f"Error getting available cash: {e}")
            return Decimal(0)

    def init_sod_cash(self, amount: Decimal) -> None:
        """Set the start of day cash balance."""
        self.sod_cash = amount

    def calculate_weighted_notional(self, symbol: str, weight: float) -> Decimal:
        """Calculate the weighted notional for a given symbol and weight."""
        try:
            available_cash = self.cash_service.total_cash()
            available_notional = min((self.sod_cash * weight), available_cash)
            self.logger.info(
                f"Calculated weighted notional for {symbol}: {available_notional} of available{available_cash}"
            )
            return Decimal(available_notional)
        except Exception as e:
            self.logger.error(f"Error calculating weighted notional for {symbol}: {e}")
            return Decimal(0)

    def fetch_order_by_id(self, order_id: str) -> DBOrder | None:
        """Fetch an order by its ID."""
        try:
            return self.order_service.fetch_order_by_id(order_id)
        except Exception as e:
            self.logger.error(f"Error fetching order {order_id}: {e}")
            return None

    def submit_equity_order(self, order: EquityBaseOrder, enriched_data: dict) -> None:
        """Submit a new order."""
        try:
            order_id = self.order_service.submit_order(order)
            self.enriched_data_service.insert_enriched_data(
                order_id=order_id, enriched_data=enriched_data
            )
            self.logger.info(f"Submitted order {order} | {order_id}.")
        except Exception as e:
            self.logger.error(f"Error submitting order {order}: {e}")

    def update_order(
        self,
        order_id: str,
        status: str,
        quantity: int | None = None,
        price: float | None = None,
    ) -> None:
        """Update an existing order."""
        try:
            self.order_service.update_order(order_id, status, quantity, price)
            self.logger.info(f"Updated order {order_id} to status {status}.")
        except Exception as e:
            self.logger.error(f"Error updating order {order_id}: {e}")
