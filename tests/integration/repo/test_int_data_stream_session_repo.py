from datetime import datetime, timezone

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
    session_id = await repo.insert_data_stream_session(
        stream_type="test_stream",
        symbol="TEST",
        strategy_name="test_strategy",
        start_time=datetime.now(timezone.utc),
    )
    assert session_id != -1
    # Fetch
    sessions = repo.fetch_data_stream_session_by_timestamp(
        datetime.now(timezone.utc) - datetime.timedelta(days=1),
        datetime.now(timezone.utc) + datetime.timedelta(days=1),
    )
    assert any(s.id == session_id for s in sessions)
    # Update
    end_time = datetime.now(timezone.utc)
    updated = repo.update_data_stream_session_end_time(session_id, end_time)
    assert updated >= 0
    # Cleanup
    deleted = repo.delete_all_data_stream_sessions()
    assert deleted >= 1
