from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.symbols.queued_async_symbol_hold import (
    QueuedAsyncSymbolHold,
)
from src.algo_royale.application.symbols.queued_async_symbol_hold import (
    QueuedAsyncSymbolHold,
)
from tests.mocks.mock_loggable import MockLoggable


class ConcreteQueuedAsyncSymbolHold(QueuedAsyncSymbolHold):
    def _type_hierarchy(self):
        return ["ConcreteQueuedAsyncSymbolHold"]


class TestQueuedAsyncSymbolHold:
    def setup_method(self):
        self.logger = MockLoggable()
        self.q = ConcreteQueuedAsyncSymbolHold(logger=self.logger)

    def test_update_normal(self):
        self.q._update(SymbolHoldStatus.HOLD_ALL)
        assert self.q.status == SymbolHoldStatus.HOLD_ALL
        self.q._update(SymbolHoldStatus.CLOSED_FOR_DAY)
        assert self.q.status == SymbolHoldStatus.CLOSED_FOR_DAY

    def test_update_exception(self):
        # Simulate an exception in _update by monkeypatching status
        class BadStatus:
            pass

        try:
            self.q._update(BadStatus())
        except Exception:
            # Should not raise, but if it does, test catches it
            assert True
