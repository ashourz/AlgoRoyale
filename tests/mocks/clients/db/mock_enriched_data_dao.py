from uuid import UUID

from algo_royale.clients.db.dao.enriched_data_dao import EnrichedDataDAO
from algo_royale.models.db.db_enriched_data import DBEnrichedData


class MockEnrichedDataDAO(EnrichedDataDAO):
    def __init__(self):
        self.base_enriched_data = DBEnrichedData(
            id=UUID("123e4567-e89b-12d3-a456-426614174100"),
            order_id=UUID("123e4567-e89b-12d3-a456-426614174002"),
            market_timestamp="2025-09-16T12:00:00Z",
            symbol="AAPL",
            market="NASDAQ",
            volume=10000.0,
            open_price=150.0,
            high_price=155.0,
            low_price=149.0,
            close_price=154.0,
            num_trades=500,
            volume_weighted_price=152.5,
            pct_return=0.026,
            log_return=0.0257,
            sma_10=151.0,
            sma_20=150.5,
            sma_50=149.8,
            sma_100=148.0,
            sma_150=147.5,
            sma_200=146.0,
            macd=1.2,
            macd_signal=1.1,
            rsi=55.0,
            ema_9=152.0,
            ema_10=151.8,
            ema_12=151.5,
            ema_20=150.9,
            ema_26=150.2,
            ema_50=149.5,
            ema_100=148.2,
            ema_150=147.8,
            ema_200=146.5,
            volatility_10=0.02,
            volatility_20=0.021,
            volatility_50=0.019,
            atr_14=2.5,
            hist_volatility_20=0.018,
            range=6.0,
            body=4.0,
            upper_wick=1.0,
            lower_wick=1.0,
            vol_ma_10=9800.0,
            vol_ma_20=9700.0,
            vol_ma_50=9500.0,
            vol_ma_100=9400.0,
            vol_ma_200=9300.0,
            vol_change=0.05,
            vwap_10=152.2,
            vwap_20=151.9,
            vwap_50=151.0,
            vwap_100=150.5,
            vwap_150=150.0,
            vwap_200=149.5,
            hour=12,
            day_of_week=1,
            adx=25.0,
            momentum_10=2.0,
            roc_10=0.013,
            stochastic_k=80.0,
            stochastic_d=78.0,
            bollinger_upper=156.0,
            bollinger_lower=148.0,
            bollinger_width=8.0,
            gap=0.5,
            high_low_ratio=1.04,
            obv=500000.0,
            adl=250000.0,
        )
        self.test_enriched_data = self.base_enriched_data

    def reset_enriched_data(self):
        self.test_enriched_data = self.base_enriched_data

    def reset(self):
        self.reset_enriched_data()

    def fetch_enriched_data_by_order_id(self, order_id: UUID) -> list[DBEnrichedData]:
        return [self.test_enriched_data]

    def insert_enriched_data(self, order_id: UUID, enriched_data: dict) -> int:
        return 1

    def delete_all_enriched_data(self) -> int:
        return 1
