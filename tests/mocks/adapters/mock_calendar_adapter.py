from algo_royale.adapters.trading.calendar_adapter import CalendarAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockCalendarAdapter(CalendarAdapter):
    def __init__(self):
        logger = MockLoggable()
        super().__init__(logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_calendar(self, *args, **kwargs):
        if self.return_empty:
            return []
        return [{"date": "2024-01-01", "open": "09:30", "close": "16:00"}]
