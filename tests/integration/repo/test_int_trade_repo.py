from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

## Removed unused import
from algo_royale.di.application_container import ApplicationContainer


@pytest.fixture
def repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    repo = application.repo_container.trade_repo
    yield repo
    repo.delete_all_trades()


def test_trade_repo_methods(repo):
    # Insert
    trade_id = repo.insert_trade(
        symbol="TEST",
        action="BUY",
        settlement_date=datetime.utcnow(),
        price=Decimal("1.23"),
        quantity=1,
        executed_at=datetime.utcnow(),
        order_id=uuid4(),
    )
    assert trade_id != -1
    # Fetch unsettled trades
    trades = repo.fetch_unsettled_trades()
    assert isinstance(trades, list)
    # Add more lifecycle/cleanup logic if DAO supports it
