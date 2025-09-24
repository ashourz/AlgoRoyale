from uuid import uuid4

import pytest

from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.repo.order_repo import DBOrderStatus


@pytest.fixture
def repo():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    # Ensure the database and tables exist
    application.repo_container.db_container.db_connection(create_if_not_exists=True)
    repo = application.repo_container.order_repo
    yield repo
    # Add cleanup if available: repo.dao.delete_all_orders()
    db = application.repo_container.db_container
    db.close()


def test_order_repo_methods(repo):
    order_id = uuid4()
    user_id = "test_user"
    account_id = "test_account"
    # Fetch by id
    orders = repo.fetch_order_by_id(order_id, user_id, account_id)
    assert isinstance(orders, list)
    # Fetch by status
    orders_by_status = repo.fetch_orders_by_status([DBOrderStatus.NEW])
    assert isinstance(orders_by_status, list)
    # Add more lifecycle/cleanup logic if DAO supports it
