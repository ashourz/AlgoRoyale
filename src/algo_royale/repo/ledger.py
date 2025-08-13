import datetime
from decimal import Decimal
from logging import Logger
from algo_royale.logging.loggable import Loggable
from algo_royale.adapters.account_cash_adapter import AccountCashAdapter
from algo_royale.repo.order_repo import OrderRepo
from algo_royale.repo.positions_repo import PositionsRepo
from algo_royale.repo.trade_repo import TradeDirection, TradeEntry, TradeRepo


class Ledger:
    def __init__(
        self, 
        cash_repo: AccountCashAdapter,
        orderRepo: OrderRepo,
        tradeRepo: TradeRepo,
        positionsRepo: PositionsRepo,
        logger: Loggable
    ):
        self.entries = []
        self.cash_repo = cash_repo
        self.order_repo = orderRepo
        self.trade_repo = tradeRepo
        self.positions_repo = positionsRepo
        self.logger = logger

    def add_trade_entry(self, trade_entry: TradeEntry):
        """Add a trade entry to the ledger."""
        if not isinstance(trade_entry, TradeEntry):
            raise TypeError("trade_entry must be an instance of TradeEntry")
        self.order_service.add_order_entry(
        self.entries.append(trade_entry)

    def add_order_entry(
        self, symbol: str, direction: TradeDirection, execution_price: Decimal, shares: int,
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
        
    
