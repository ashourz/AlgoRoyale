import datetime

import pytest

## Removed unused import
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


@pytest.fixture
def repo():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    # Ensure the database and tables exist
    db_container = application.repo_container.db_container
    db_container.register_user()
    application.repo_container.db_container.db_connection(create_if_not_exists=True)
    repo = application.repo_container.data_stream_session_repo
    yield repo
    repo.delete_all_data_stream_sessions()
    db_container.close()


def test_data_stream_session_lifecycle(repo):
    # Insert
    session_id = repo.insert_data_stream_session(
        stream_type="test_stream",
        symbol="TEST",
        strategy_name="test_strategy",
        start_time=datetime.datetime.utcnow(),
    )
    assert session_id != -1
    # Fetch
    sessions = repo.fetch_data_stream_session_by_timestamp(
        datetime.datetime.utcnow() - datetime.timedelta(days=1),
        datetime.datetime.utcnow() + datetime.timedelta(days=1),
    )
    assert any(s.id == session_id for s in sessions)
    # Update
    end_time = datetime.datetime.utcnow()
    updated = repo.update_data_stream_session_end_time(session_id, end_time)
    assert updated >= 0
    # Cleanup
    deleted = repo.delete_all_data_stream_sessions()
    assert deleted >= 1
