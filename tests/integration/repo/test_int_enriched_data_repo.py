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
    # Ensure the database and tables exist
    db_container = application.repo_container.db_container
    db_container.register_user()
    application.repo_container.db_container.db_connection(create_if_not_exists=True)
    repo = application.repo_container.enriched_data_repo
    yield repo
    repo.delete_all_enriched_data()
    db_container.close()


def test_enriched_data_lifecycle(repo):
    order_id = uuid4()
    enriched_data = {"key": "value"}
    # Insert
    data_id = repo.insert_enriched_data(order_id, enriched_data)
    assert data_id != -1
    # Fetch
    data = repo.fetch_enriched_data_by_order_id(order_id)
    assert data
    # Cleanup
    deleted = repo.delete_all_enriched_data()
    assert deleted >= 1
