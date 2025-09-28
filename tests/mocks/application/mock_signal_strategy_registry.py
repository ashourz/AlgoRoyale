from algo_royale.application.strategies.signal_strategy_registry import (
    SignalStrategyRegistry,
)
from algo_royale.backtester.strategy.signal.combined_weighted_signal_strategy import (
    CombinedWeightedSignalStrategy,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.strategy_factory.signal.mock_signal_strategy_factory import (
    MockSignalStrategyFactory,
)
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_symbol_service import MockSymbolService


class MockSignalStrategyRegistry(SignalStrategyRegistry):
    def __init__(self):
        super().__init__(
            symbol_service=MockSymbolService(),
            stage_data_manager=MockStageDataManager(),
            evaluation_json_filename="mock_evaluation.json",
            viable_strategies_path="mock_viable_strategies",
            signal_strategy_factory=MockSignalStrategyFactory(),
            logger=MockLoggable(),
            combined_buy_threshold=0.5,
            combined_sell_threshold=0.5,
        )
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False

    def get_combined_weighted_signal_strategy(
        self, symbol
    ) -> CombinedWeightedSignalStrategy | None:
        if self.return_empty:
            return None
        return CombinedWeightedSignalStrategy(
            buffered_strategies={},
            buy_threshold=0.5,
            sell_threshold=0.5,
        )
