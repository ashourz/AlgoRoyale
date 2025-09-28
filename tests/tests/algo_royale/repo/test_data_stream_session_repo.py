import datetime

import pytest

from algo_royale.repo.data_stream_session_repo import DataStreamSessionRepo
from tests.mocks.repo.mock_data_stream_session_repo import MockDataStreamSessionRepo


@pytest.fixture
def data_stream_session_repo():
    adapter = MockDataStreamSessionRepo()
    yield adapter


@pytest.mark.asyncio
class TestDataStreamSessionRepo:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, data_stream_session_repo: MockDataStreamSessionRepo):
        print("Setup")
        data_stream_session_repo.reset_return_empty()
        data_stream_session_repo.reset_raise_exception()
        data_stream_session_repo.reset_dao()
        yield
        print("Teardown")
        data_stream_session_repo.reset_return_empty()
        data_stream_session_repo.reset_raise_exception()
        data_stream_session_repo.reset_dao()

    async def test_fetch_data_stream_session_by_timestamp_normal(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        start = datetime.datetime.now() - datetime.timedelta(days=1)
        end = datetime.datetime.now()
        sessions = data_stream_session_repo.fetch_data_stream_session_by_timestamp(
            start, end
        )
        assert len(sessions) == 1
        assert sessions[0].symbol == "AAPL"

    async def test_fetch_data_stream_session_by_timestamp_empty(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        data_stream_session_repo._return_empty = True
        start = datetime.datetime.now() - datetime.timedelta(days=1)
        end = datetime.datetime.now()
        sessions = data_stream_session_repo.fetch_data_stream_session_by_timestamp(
            start, end
        )
        assert len(sessions) == 0

    async def test_fetch_data_stream_session_by_timestamp_exception(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        data_stream_session_repo._raise_exception = True
        start = datetime.datetime.now() - datetime.timedelta(days=1)
        end = datetime.datetime.now()
        with pytest.raises(ValueError) as excinfo:
            data_stream_session_repo.fetch_data_stream_session_by_timestamp(start, end)
        assert "Database error" in str(excinfo.value)

    async def test_insert_data_stream_session_normal(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        start_time = datetime.datetime.now()
        inserted_id = data_stream_session_repo.insert_data_stream_session(
            stream_type="live",
            symbol="AAPL",
            strategy_name="test_strategy",
            start_time=start_time,
        )
        assert inserted_id is not None

    async def test_insert_data_stream_session_exception(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        data_stream_session_repo._raise_exception = True
        start_time = datetime.datetime.now()
        with pytest.raises(ValueError) as excinfo:
            data_stream_session_repo.insert_data_stream_session(
                stream_type="live",
                symbol="AAPL",
                strategy_name="test_strategy",
                start_time=start_time,
            )
        assert "Database error" in str(excinfo.value)

    async def test_update_data_stream_session_end_time_normal(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        end_time = datetime.datetime.now()
        updated = data_stream_session_repo.update_data_stream_session_end_time(
            1, end_time
        )
        assert updated == 1

    async def test_update_data_stream_session_end_time_exception(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        data_stream_session_repo._raise_exception = True
        end_time = datetime.datetime.now()
        with pytest.raises(ValueError) as excinfo:
            data_stream_session_repo.update_data_stream_session_end_time(1, end_time)
        assert "Database error" in str(excinfo.value)

    async def test_delete_all_data_stream_sessions_normal(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        deleted = data_stream_session_repo.delete_all_data_stream_sessions()
        assert deleted == 1

    async def test_delete_all_data_stream_sessions_exception(
        self, data_stream_session_repo: DataStreamSessionRepo
    ):
        data_stream_session_repo._raise_exception = True
        with pytest.raises(ValueError) as excinfo:
            data_stream_session_repo.delete_all_data_stream_sessions()
        assert "Database error" in str(excinfo.value)
