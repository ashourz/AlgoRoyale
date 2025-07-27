import datetime
from decimal import Decimal
from algo_royale.trader.cash.cash_repo import CashRepo
from algo_royale.trader.trades.trade_repo import TradeDirection, TradeEntry, TradeRepo


class Ledger:
    def __init__(
        self, 
        cash_repo: CashRepo,
        orderRepo: OrderRepo,
        tradeRepo: TradeRepo
    ):
        self.entries = []
        self.cash_repo = cash_repo
        self.order_repo = orderRepo
        self.trade_repo = tradeRepo

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
        
    
