from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

## Removed unused import
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


@pytest.fixture
def repo():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    # Ensure the database and tables exist
    application.repo_container.db_container.db_connection(create_if_not_exists=True)
    repo = application.repo_container.trade_repo
    yield repo
    # Add cleanup logic if DAO supports it
    db = application.repo_container.db_container
    db.close()


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
