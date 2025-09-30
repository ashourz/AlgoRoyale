from algo_royale.adapters.market_data.corporate_action_adapter import (
    CorporateActionAdapter,
)
from tests.mocks.clients.alpaca.mock_alpaca_corporate_action_client import (
    MockAlpacaCorporateActionClient,
)
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_clock_service import MockClockService


class MockCorporateActionAdapter(CorporateActionAdapter):
    def __init__(self):
        logger = MockLoggable()  # Or use a mock logger if needed
        client = MockAlpacaCorporateActionClient()
        super().__init__(client=client, clock_service=MockClockService(), logger=logger)

    def set_return_empty(self, value: bool):
        self.client.return_empty = value

    def reset_return_empty(self):
        self.client.return_empty = False
