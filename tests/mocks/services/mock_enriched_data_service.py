from algo_royale.services.enriched_data_service import EnrichedDataService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_enriched_data_repo import MockEnrichedDataRepo


class MockEnrichedDataService(EnrichedDataService):
    def __init__(self):
        super().__init__(
            enriched_data_repo=MockEnrichedDataRepo(),
            logger=MockLoggable(),
        )

    def set_return_empty(self, value: bool):
        self.enriched_data_repo.set_return_empty(value)

    def reset_return_empty(self):
        self.enriched_data_repo.reset_return_empty()

    def set_raise_exception(self, value: bool):
        self.enriched_data_repo.set_raise_exception(value)

    def reset_raise_exception(self):
        self.enriched_data_repo.reset_raise_exception()

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
        self.enriched_data_repo.reset_dao()
