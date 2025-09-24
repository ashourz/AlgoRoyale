import pytest

from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv

SQL_FILES = [
    "delete_all_orders.sql",
    "delete_order.sql",
    "fetch_all_orders_by_status.sql",
    "fetch_all_orders_by_symbol_and_status.sql",
    "fetch_order_by_id.sql",
    "fetch_orders_by_status.sql",
    "fetch_orders_by_symbol_and_status.sql",
    "fetch_unsettled_orders.sql",
    "insert_order.sql",
    "update_order_as_settled.sql",
    "update_order.sql",
]


@pytest.fixture
def dao():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    dao = application.repo_container.order_repo.dao
    yield dao
    db = application.repo_container.db_container
    db.close()


@pytest.mark.parametrize("sql_file", SQL_FILES)
def test_load_sql_file(dao, sql_file):
    sql = dao._load_sql(sql_file)
    assert isinstance(sql, str)
    assert len(sql) > 0
