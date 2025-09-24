import pytest

from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv

SQL_FILES = [
    "delete_all_enriched_data.sql",
    "fetch_enriched_data_by_order_id.sql",
    "insert_enriched_data.sql",
]


@pytest.fixture
def dao():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    dao = application.repo_container.enriched_data_repo.dao
    yield dao
    db = application.repo_container.db_container
    db.close()


@pytest.mark.parametrize("sql_file", SQL_FILES)
def test_load_sql_file(dao, sql_file):
    sql = dao._load_sql(sql_file)
    assert isinstance(sql, str)
    assert len(sql) > 0
