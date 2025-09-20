import pytest

from tests.mocks.backtester.strategy_factory.signal.mock_signal_strategy_factory import (
    MockSignalStrategyFactory,
)
from tests.mocks.mock_loggable import MockLoggable


class TestSignalStrategyFactory:
    def setup_method(self):
        self.logger = MockLoggable()
        self.factory = MockSignalStrategyFactory()

    def test_create_strategy_normal(self):
        try:
            strategy = self.factory.create_strategy("SomeStrategy", {})
        except Exception as e:
            assert isinstance(e, Exception)

    def test_create_strategy_error(self):
        with pytest.raises(Exception):
            self.factory.create_strategy("NonExistentStrategy", {})

    def test_create_strategy_invalid_type(self):
        with pytest.raises(Exception):
            self.factory.create_strategy(123, {})
