from uuid import UUID

import pytest

from algo_royale.services.enriched_data_service import EnrichedDataService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_enriched_data_repo import MockEnrichedDataRepo


@pytest.fixture
def enriched_data_service():
    service = EnrichedDataService(
        enriched_data_repo=MockEnrichedDataRepo(), logger=MockLoggable()
    )
    yield service


def set_enriched_data_service_raise_exception(
    enriched_data_service: EnrichedDataService, value: bool
):
    enriched_data_service.enriched_data_repo.set_raise_exception(value)


def reset_enriched_data_service_raise_exception(
    enriched_data_service: EnrichedDataService,
):
    enriched_data_service.enriched_data_repo.reset_raise_exception()


def set_enriched_data_service_return_empty(
    enriched_data_service: EnrichedDataService, value: bool
):
    enriched_data_service.enriched_data_repo.set_return_empty(value)


def reset_enriched_data_service_return_empty(
    enriched_data_service: EnrichedDataService,
):
    enriched_data_service.enriched_data_repo.reset_return_empty()


def reset_enriched_data_service(enriched_data_service: EnrichedDataService):
    enriched_data_service.enriched_data_repo.reset()


@pytest.mark.asyncio
class TestEnrichedDataService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, enriched_data_service: EnrichedDataService):
        print("Setup")
        reset_enriched_data_service(enriched_data_service)
        yield
        print("Teardown")
        reset_enriched_data_service(enriched_data_service)

    def test_insert_enriched_data_normal(
        self, enriched_data_service: EnrichedDataService
    ):
        order_id = "order123"
        enriched_data = {"foo": "bar"}
        result = enriched_data_service.insert_enriched_data(order_id, enriched_data)
        assert (
            result == UUID("11111111-1111-1111-1111-111111111111") or result is not None
        )

    def test_insert_enriched_data_exception(
        self, enriched_data_service: EnrichedDataService
    ):
        set_enriched_data_service_raise_exception(enriched_data_service, True)
        order_id = UUID("33333333-3333-3333-3333-333333333333")
        enriched_data = {"foo": "bar"}
        result = enriched_data_service.insert_enriched_data(order_id, enriched_data)
        assert result is None
        reset_enriched_data_service_raise_exception(enriched_data_service)

    def test_fetch_enriched_data_by_order_id_normal(
        self, enriched_data_service: EnrichedDataService
    ):
        order_id = UUID("44444444-4444-4444-4444-444444444444")
        result = enriched_data_service.fetch_enriched_data_by_order_id(order_id)
        assert isinstance(result, list)

    def test_fetch_enriched_data_by_order_id_exception(
        self, enriched_data_service: EnrichedDataService
    ):
        set_enriched_data_service_raise_exception(enriched_data_service, True)
        order_id = UUID("55555555-5555-5555-5555-555555555555")
        result = enriched_data_service.fetch_enriched_data_by_order_id(order_id)
        assert result == []
        reset_enriched_data_service_raise_exception(enriched_data_service)

    def test_delete_all_enriched_data_normal(
        self, enriched_data_service: EnrichedDataService
    ):
        result = enriched_data_service.delete_all_enriched_data()
        assert result == 1 or result > 0

    def test_delete_all_enriched_data_exception(
        self, enriched_data_service: EnrichedDataService
    ):
        set_enriched_data_service_raise_exception(enriched_data_service, True)
        result = enriched_data_service.delete_all_enriched_data()
        assert result == -1
        reset_enriched_data_service_raise_exception(enriched_data_service)
