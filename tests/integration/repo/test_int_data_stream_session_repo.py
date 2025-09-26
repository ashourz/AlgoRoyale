from datetime import datetime

import pytest

from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


@pytest.fixture(scope="session")
def application():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    yield application
    application.repo_container.db_container.close()


@pytest.fixture(scope="session", autouse=True)
def environment_setup(application):
    logger = application.repo_container.db_container.logger
    logger.debug("Starting environment setup...")
    db_container = application.repo_container.db_container
    db_container.setup_environment()
    yield True
    db_container.teardown_environment()


@pytest.fixture
def repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    repo = application.repo_container.data_stream_session_repo
    yield repo
    repo.delete_all_data_stream_sessions()


def test_data_stream_session_lifecycle(repo):
    # Insert
    session_id = repo.insert_data_stream_session(
        stream_type="test_stream",
        symbol="TEST",
        strategy_name="test_strategy",
        start_time=datetime.now(datetime.timezone.utc),
    )
    assert session_id != -1
    # Fetch
    sessions = repo.fetch_data_stream_session_by_timestamp(
        datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1),
        datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
    )
    assert any(s.id == session_id for s in sessions)
    # Update
    end_time = datetime.now(datetime.timezone.utc)
    updated = repo.update_data_stream_session_end_time(session_id, end_time)
    assert updated >= 0
    # Cleanup
    deleted = repo.delete_all_data_stream_sessions()
    assert deleted >= 1
