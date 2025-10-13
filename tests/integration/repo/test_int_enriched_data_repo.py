from decimal import Decimal

import pytest

## Removed unused import
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.repo.order_repo import DBOrderStatus, OrderAction, OrderType


@pytest.fixture
def enriched_data_repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    repo = application.repo_container.enriched_data_repo
    yield repo
    repo.delete_all_enriched_data()


@pytest.fixture
def order_repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    repo = application.repo_container.order_repo
    yield repo
    repo.delete_all_orders()


def test_enriched_data_lifecycle(enriched_data_repo, order_repo):
    enriched_data = {
        "market_timestamp": "2025-09-27 12:00:00",
        "symbol": "AAPL",
        "market": "NASDAQ",
        "volume": 1000.0,
        "open_price": 150.0,
        "high_price": 155.0,
        "low_price": 149.0,
        "close_price": 154.0,
        "num_trades": 10,
        "volume_weighted_price": 152.0,
        "pct_return": 0.02,
        "log_return": 0.0198,
        "sma_10": 151.0,
        "sma_20": 150.5,
        "sma_50": 149.8,
        "sma_100": 148.0,
        "sma_150": 147.5,
        "sma_200": 146.0,
        "macd": 0.5,
        "macd_signal": 0.4,
        "rsi": 55.0,
        "ema_9": 150.8,
        "ema_10": 150.7,
        "ema_12": 150.6,
        "ema_20": 150.5,
        "ema_26": 150.4,
        "ema_50": 150.3,
        "ema_100": 150.2,
        "ema_150": 150.1,
        "ema_200": 150.0,
        "volatility_10": 1.2,
        "volatility_20": 1.3,
        "volatility_50": 1.4,
        "atr_14": 1.1,
        "hist_volatility_20": 1.5,
        "range": 6.0,
        "body": 5.0,
        "upper_wick": 1.0,
        "lower_wick": 0.5,
        "vol_ma_10": 950.0,
        "vol_ma_20": 900.0,
        "vol_ma_50": 850.0,
        "vol_ma_100": 800.0,
        "vol_ma_200": 750.0,
        "vol_change": 0.05,
        "vwap_10": 151.5,
        "vwap_20": 151.0,
        "vwap_50": 150.5,
        "vwap_100": 150.0,
        "vwap_150": 149.5,
        "vwap_200": 149.0,
        "hour": 12,
        "day_of_week": 5,
        "adx": 25.0,
        "momentum_10": 0.8,
        "roc_10": 0.03,
        "stochastic_k": 80.0,
        "stochastic_d": 75.0,
        "bollinger_upper": 156.0,
        "bollinger_lower": 144.0,
        "bollinger_width": 12.0,
        "gap": 0.2,
        "high_low_ratio": 1.04,
        "obv": 10000.0,
        "adl": 5000.0,
    }
    # Insert an order to link with the trade
    order_id = order_repo.insert_order(
        symbol="TEST",
        order_type=OrderType.MARKET,
        status=DBOrderStatus.FILL,
        action=OrderAction.BUY,
        quantity=1,
        price=Decimal("1.23"),
    )
    print(f"Inserted order ID: {order_id}")
    # Insert
    data_id = enriched_data_repo.insert_enriched_data(order_id, enriched_data)
    assert data_id != -1
    # Fetch
    data = enriched_data_repo.fetch_enriched_data_by_order_id(order_id)
    assert data
    # Cleanup
    deleted = enriched_data_repo.delete_all_enriched_data()
    assert deleted >= 1
