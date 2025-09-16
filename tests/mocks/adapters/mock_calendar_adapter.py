from algo_royale.adapters.trading.calendar_adapter import CalendarAdapter
from tests.mocks.clients.mock_alpaca_calendar_client import MockAlpacaCalendarClient
from tests.mocks.mock_loggable import MockLoggable


class MockCalendarAdapter(CalendarAdapter):
    def __init__(self):
        client = MockAlpacaCalendarClient()
        logger = MockLoggable()
        super().__init__(calendar_client=client, logger=logger)
        self.return_empty = False
        self.throw_exception = False

    def set_return_empty(self, value: bool):
        self.calendar_client.return_empty = value

    def reset_return_empty(self):
        self.calendar_client.return_empty = False

    def set_throw_exception(self, value: bool):
        self.calendar_client.throw_exception = value

    def reset_throw_exception(self):
        self.calendar_client.throw_exception = False
