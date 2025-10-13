from datetime import datetime, timedelta, timezone

import pytest

from algo_royale.di.application_container import ApplicationContainer


@pytest.fixture
def repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    repo = application.repo_container.data_stream_session_repo
    yield repo
    repo.delete_all_data_stream_sessions()


@pytest.mark.asyncio
async def test_data_stream_session_lifecycle(repo):
    # Insert
    session_id = repo.insert_data_stream_session(
        stream_class_name="test_stream",
        symbol="TEST",
        start_time=datetime.now(timezone.utc),
    )
    session_id = session_id[0] if isinstance(session_id, tuple) else session_id
    print(f"Inserted session ID: {session_id}")
    assert session_id != -1
    # Fetch
    sessions = repo.fetch_data_stream_session_by_timestamp(
        start_timestamp=datetime.now(timezone.utc) - timedelta(days=1),
        end_timestamp=datetime.now(timezone.utc) + timedelta(days=1),
    )
    print(f"Fetched sessions: {sessions}")
    assert any(str(s.id) == str(session_id) for s in sessions)
    # Update
    end_time = datetime.now(timezone.utc)
    updated = repo.update_data_stream_session_end_time(session_id, end_time)
    assert updated >= 0
    # Cleanup
    deleted = repo.delete_all_data_stream_sessions()
    assert deleted >= 1
