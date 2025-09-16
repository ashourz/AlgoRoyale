from uuid import UUID, uuid4

import pytest

from tests.mocks.repo.mock_enriched_data_repo import MockEnrichedDataRepo


@pytest.fixture
def enriched_data_repo():
    adapter = MockEnrichedDataRepo()
    yield adapter


@pytest.mark.asyncio
class TestEnrichedDataRepo:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, enriched_data_repo: MockEnrichedDataRepo):
        print("Setup")
        enriched_data_repo.reset_return_empty()
        enriched_data_repo.reset_raise_exception()
        enriched_data_repo.reset_dao()
        yield
        print("Teardown")
        enriched_data_repo.reset_return_empty()
        enriched_data_repo.reset_raise_exception()
        enriched_data_repo.reset_dao()

    async def test_fetch_enriched_data_by_order_id_normal(self, enriched_data_repo):
        order_id = uuid4()
        data = enriched_data_repo.fetch_enriched_data_by_order_id(order_id)
        assert len(data) == 1
        assert data[0].order_id == order_id or isinstance(data[0].order_id, UUID)

    async def test_fetch_enriched_data_by_order_id_empty(self, enriched_data_repo):
        enriched_data_repo._return_empty = True
        order_id = uuid4()
        data = enriched_data_repo.fetch_enriched_data_by_order_id(order_id)
        assert len(data) == 0

    async def test_fetch_enriched_data_by_order_id_exception(self, enriched_data_repo):
        enriched_data_repo._raise_exception = True
        order_id = uuid4()
        with pytest.raises(ValueError) as excinfo:
            enriched_data_repo.fetch_enriched_data_by_order_id(order_id)
        assert "Database error" in str(excinfo.value)

    async def test_insert_enriched_data_normal(self, enriched_data_repo):
        order_id = uuid4()
        enriched_data = {"symbol": "AAPL"}
        inserted_id = enriched_data_repo.insert_enriched_data(order_id, enriched_data)
        assert inserted_id == 1

    async def test_insert_enriched_data_exception(self, enriched_data_repo):
        enriched_data_repo._raise_exception = True
        order_id = uuid4()
        enriched_data = {"symbol": "AAPL"}
        with pytest.raises(ValueError) as excinfo:
            enriched_data_repo.insert_enriched_data(order_id, enriched_data)
        assert "Database error" in str(excinfo.value)

    async def test_delete_all_enriched_data_normal(self, enriched_data_repo):
        deleted = enriched_data_repo.delete_all_enriched_data()
        assert deleted == 1

    async def test_delete_all_enriched_data_exception(self, enriched_data_repo):
        enriched_data_repo._raise_exception = True
        with pytest.raises(ValueError) as excinfo:
            enriched_data_repo.delete_all_enriched_data()
        assert "Database error" in str(excinfo.value)
