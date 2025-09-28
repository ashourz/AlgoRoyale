from algo_royale.application.strategies.portfolio_strategy_registry import (
    PortfolioStrategyRegistry,
)
from algo_royale.backtester.strategy.portfolio.buffered_components.buffered_portfolio_strategy import (
    BufferedPortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.mock.mock_portfolio_strategy import (
    MockPortfolioStrategy,
)
from tests.mocks.backtester.data_preparer.mock_asset_matrix_preparer import (
    MockAssetMatrixPreparer,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.strategy_factory.portfolio.mock_portfolio_strategy_factory import (
    MockPortfolioStrategyFactory,
)
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_symbol_service import MockSymbolService


class MockPortfolioStrategyRegistry(PortfolioStrategyRegistry):
    def __init__(self):
        super().__init__(
            symbol_service=MockSymbolService(),
            stage_data_manager=MockStageDataManager(),
            evaluation_json_filename="mock_evaluation.json",
            viable_strategies_path="mock_viable_strategies",
            portfolio_strategy_factory=MockPortfolioStrategyFactory(),
            logger=MockLoggable(),
        )
        self.return_empty = False
        self.last_symbols = set()

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False

    def get_buffered_portfolio_strategy(
        self, symbols
    ) -> BufferedPortfolioStrategy | None:
        self.last_symbols = set(symbols) if symbols is not None else set()
        if self.return_empty:
            return None
        return BufferedPortfolioStrategy(
            strategy=MockPortfolioStrategy(),
            asset_matrix_preparer=MockAssetMatrixPreparer(),
            logger=MockLoggable(),
        )
