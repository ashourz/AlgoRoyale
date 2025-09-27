import pytest

from algo_royale.di.application_container import ApplicationContainer

SQL_FILES = [
    "delete_all_enriched_data.sql",
    "fetch_enriched_data_by_order_id.sql",
    "insert_enriched_data.sql",
]


@pytest.fixture
def dao(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    dao = application.repo_container.enriched_data_repo.dao
    yield dao
    db = application.repo_container.db_container
    db.close()


@pytest.mark.parametrize("sql_file", SQL_FILES)
def test_load_sql_file(dao, sql_file):
    sql = dao._load_sql(sql_file)
    assert isinstance(sql, str)
    assert len(sql) > 0
