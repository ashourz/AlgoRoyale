from uuid import uuid4

import pytest

from algo_royale.di.application_container import ApplicationContainer
from algo_royale.repo.order_repo import DBOrderStatus


@pytest.fixture
def repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    # Ensure the database and tables exist
    db_container = application.repo_container.db_container
    db_container.register_user()
    application.repo_container.db_container.db_connection(create_if_not_exists=True)
    repo = application.repo_container.order_repo
    yield repo
    # Add cleanup if available: repo.dao.delete_all_orders()
    db_container.close()


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
