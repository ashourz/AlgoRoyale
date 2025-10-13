from datetime import datetime
from decimal import Decimal
from uuid import UUID

import pytest

## Removed unused import
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.models.alpaca_trading.enums.enums import OrderType
from algo_royale.repo.order_repo import DBOrderStatus, OrderAction, OrderRepo


@pytest.fixture
def trade_repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    repo = application.repo_container.trade_repo
    yield repo
    repo.delete_all_trades()


@pytest.fixture
def order_repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    repo = application.repo_container.order_repo
    yield repo
    repo.delete_all_orders()


def test_trade_repo_methods(trade_repo, order_repo: OrderRepo):
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
    trade_id = trade_repo.insert_trade(
        external_id="mocked_external_id_001",
        symbol="TEST",
        action=OrderAction.BUY,
        settlement_date=datetime.utcnow(),
        price=Decimal("1.23"),
        quantity=1,
        executed_at=datetime.utcnow(),
        order_id=UUID(order_id),
    )
    assert trade_id != -1
    # Fetch unsettled trades
    trades = trade_repo.fetch_unsettled_trades()
    assert isinstance(trades, list)
    # Add more lifecycle/cleanup logic if DAO supports it
