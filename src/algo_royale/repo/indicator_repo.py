## service\indicator_service.py
from datetime import datetime
from decimal import Decimal

from algo_royale.clients.db.dao.indicator_dao import IndicatorRepo


class IndicatorRepo:
    def __init__(self, dao: IndicatorRepo):
        self.dao = dao

    def create_indicator(
        self,
        trade_id: int,
        rsi: Decimal,
        macd: Decimal,
        macd_signal: Decimal,
        volume: Decimal,
        bollinger_upper: Decimal,
        bollinger_lower: Decimal,
        atr: Decimal,
        price: Decimal,
        ema_short: Decimal,
        ema_long: Decimal,
        recorded_at: datetime,
    ) -> None:
        """Insert indicators for a specific trade."""
        self.dao.insert_indicator(
            trade_id,
            rsi,
            macd,
            macd_signal,
            volume,
            bollinger_upper,
            bollinger_lower,
            atr,
            price,
            ema_short,
            ema_long,
            recorded_at,
        )

    def get_indicators_by_trade_id(self, trade_id: int):
        """Fetch indicators for a trade by trade ID."""
        return self.dao.fetch_indicators_by_trade_id(trade_id)

    def get_indicators_by_trade_id_and_date(
        self, trade_id: int, start_date: datetime, end_date: datetime
    ):
        """Fetch indicators for a trade by trade ID and date range."""
        return self.dao.fetch_indicators_by_trade_id_and_date(
            trade_id, start_date, end_date
        )

    def update_indicator(
        self,
        indicator_id: int,
        rsi: Decimal,
        macd: Decimal,
        macd_signal: Decimal,
        volume: Decimal,
        bollinger_upper: Decimal,
        bollinger_lower: Decimal,
        atr: Decimal,
        price: Decimal,
        ema_short: Decimal,
        ema_long: Decimal,
        recorded_at: datetime,
    ) -> None:
        """Update existing indicators."""
        self.dao.update_indicator(
            indicator_id,
            rsi,
            macd,
            macd_signal,
            volume,
            bollinger_upper,
            bollinger_lower,
            atr,
            price,
            ema_short,
            ema_long,
            recorded_at,
        )

    def delete_indicator(self, indicator_id: int) -> None:
        """Delete indicators by ID."""
        self.dao.delete_indicator(indicator_id)
