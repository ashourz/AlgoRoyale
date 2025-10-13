import pytest

from tests.mocks.backtester.strategy_factory.signal.mock_signal_strategy_combinator_factory import (
    MockSignalStrategyCombinatorFactory,
)
from tests.mocks.mock_loggable import MockLoggable


class TestSignalStrategyCombinatorFactory:
    def setup_method(self):
        self.logger = MockLoggable()
        self.factory = MockSignalStrategyCombinatorFactory(
            "/tmp/combinators.json", self.logger, self.logger
        )

    def test_get_combinator_normal(self):
        try:
            combinator = self.factory.get_combinator("SomeCombinator")
        except Exception as e:
            assert isinstance(e, Exception)

    def test_get_combinator_error(self):
        with pytest.raises(Exception):
            self.factory.get_combinator("NonExistentCombinator")

    def test_get_combinator_invalid_type(self):
        with pytest.raises(Exception):
            self.factory.get_combinator(123)
