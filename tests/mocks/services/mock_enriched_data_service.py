from uuid import UUID

from algo_royale.services.enriched_data_service import EnrichedDataService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_enriched_data_repo import MockEnrichedDataRepo


class MockEnrichedDataService(EnrichedDataService):
    def __init__(self):
        super().__init__(
            enriched_data_repo=MockEnrichedDataRepo(),
            logger=MockLoggable(),
        )
        self.return_empty = False
        self.raise_exception = False
        self.mock_enriched_data = {"key": "value"}

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()

    def insert_enriched_data(self, order_id, enriched_data) -> UUID | None:
        if self.raise_exception:
            return None
        if self.return_empty:
            return UUID("00000000-0000-0000-0000-000000000000")
        return UUID("11111111-1111-1111-1111-111111111111")

    def fetch_enriched_data_by_order_id(self, order_id):
        if self.raise_exception:
            return []
        if self.return_empty:
            return []
        return [self.mock_enriched_data]

    def delete_all_enriched_data(self):
        if self.raise_exception:
            return -1
        if self.return_empty:
            return
        return 1
