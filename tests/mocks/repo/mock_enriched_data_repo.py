from uuid import UUID

from algo_royale.models.db.db_enriched_data import DBEnrichedData
from algo_royale.repo.enriched_data_repo import EnrichedDataRepo
from tests.mocks.clients.db.mock_enriched_data_dao import MockEnrichedDataDAO
from tests.mocks.mock_loggable import MockLoggable


class MockEnrichedDataRepo(EnrichedDataRepo):
    def __init__(self):
        self.dao = MockEnrichedDataDAO()
        self.logger = MockLoggable()
        self.user_id = "user_1"
        self.account_id = "account_1"
        super().__init__(
            dao=self.dao,
            logger=self.logger,
            user_id=self.user_id,
            account_id=self.account_id,
        )
        self._return_empty = False
        self._raise_exception = False

    def reset_return_empty(self):
        self._return_empty = False

    def reset_raise_exception(self):
        self._raise_exception = False

    def reset_dao(self):
        self.dao.reset()

    def fetch_enriched_data_by_order_id(self, order_id: UUID) -> list[DBEnrichedData]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_enriched_data_by_order_id(order_id)

    def insert_enriched_data(self, order_id: UUID, enriched_data: dict) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.insert_enriched_data(
            order_id, enriched_data, self.user_id, self.account_id
        )

    def delete_all_enriched_data(self) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.delete_all_enriched_data()
