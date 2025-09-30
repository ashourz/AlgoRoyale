import pytest

from algo_royale.di.application_container import ApplicationContainer

SQL_FILES = [
    "delete_all_trades.sql",
    "delete_trade.sql",
    "fetch_open_positions.sql",
    "fetch_trades_by_date_range.sql",
    "fetch_trades_by_order_id.sql",
    "fetch_unsettled_trades.sql",
    "insert_trade.sql",
    "update_settled_trades.sql",
    "update_trade.sql",
]


@pytest.fixture
def dao(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    dao = application.repo_container.trade_repo.dao
    yield dao
    db = application.repo_container.db_container
    db.close()


@pytest.mark.parametrize("sql_file", SQL_FILES)
def test_load_sql_file(dao, sql_file):
    sql = dao._load_sql(sql_file)
    assert isinstance(sql, str)
    assert len(sql) > 0
