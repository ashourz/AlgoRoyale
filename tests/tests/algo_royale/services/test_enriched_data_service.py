import pytest

from tests.mocks.services.mock_enriched_data_service import MockEnrichedDataService


@pytest.fixture
def enriched_data_service():
    service = MockEnrichedDataService()
    yield service


@pytest.mark.asyncio
class TestEnrichedDataService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, enriched_data_service: MockEnrichedDataService):
        print("Setup")
        enriched_data_service.reset()
        yield
        print("Teardown")
        enriched_data_service.reset()

    def test_insert_enriched_data_normal(self, enriched_data_service):
        order_id = "order123"
        enriched_data = {"foo": "bar"}
        result = enriched_data_service.insert_enriched_data(order_id, enriched_data)
        assert result == 1 or result > 0

    def test_insert_enriched_data_exception(self, enriched_data_service):
        enriched_data_service.set_raise_exception(True)
        order_id = "order123"
        enriched_data = {"foo": "bar"}
        result = enriched_data_service.insert_enriched_data(order_id, enriched_data)
        assert result == -1
        enriched_data_service.reset_raise_exception()

    def test_fetch_enriched_data_by_order_id_normal(self, enriched_data_service):
        order_id = "order123"
        result = enriched_data_service.fetch_enriched_data_by_order_id(order_id)
        assert isinstance(result, list)

    def test_fetch_enriched_data_by_order_id_exception(self, enriched_data_service):
        enriched_data_service.set_raise_exception(True)
        order_id = "order123"
        result = enriched_data_service.fetch_enriched_data_by_order_id(order_id)
        assert result == []
        enriched_data_service.reset_raise_exception()

    def test_delete_all_enriched_data_normal(self, enriched_data_service):
        result = enriched_data_service.delete_all_enriched_data()
        assert result == 1 or result > 0

    def test_delete_all_enriched_data_exception(self, enriched_data_service):
        enriched_data_service.set_raise_exception(True)
        result = enriched_data_service.delete_all_enriched_data()
        assert result == -1
        enriched_data_service.reset_raise_exception()
