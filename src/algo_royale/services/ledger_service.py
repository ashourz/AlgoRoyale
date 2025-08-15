from datetime import datetime
from decimal import Decimal

from algo_royale.logging.loggable import Loggable
from algo_royale.repo.trade_repo import TradeDirection, TradeEntry
from algo_royale.services.account_cash_service import AccountCashService
from algo_royale.services.orders_service import OrderServices
from algo_royale.services.positions_service import PositionsService
from algo_royale.services.trades_service import TradesService


class LedgerService:
    def __init__(
        self,
        cash_service: AccountCashService,
        order_service: OrderServices,
        trade_service: TradesService,
        position_service: PositionsService,
        logger: Loggable,
    ):
        self.entries = []
        self.cash_service = cash_service
        self.order_service = order_service
        self.trade_service = trade_service
        self.position_service = position_service
        self.logger = logger

    def add_order_entry(
        self,
        symbol: str,
        direction: TradeDirection,
        execution_price: Decimal,
        shares: int,
    ):
        trade_entry = TradeEntry(
            trade_id=str(len(self.entries) + 1),
            symbol=symbol,
            direction=direction,
            execution_price=execution_price,
            shares=shares,
            timestamp=datetime.now(),
        )
        self.add_trade_entry(trade_entry)
