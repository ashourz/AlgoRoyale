from algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.buffered_components.buffered_portfolio_strategy import (
    BufferedPortfolioStrategy,
)
from algo_royale.backtester.strategy_factory.portfolio.portfolio_strategy_factory import (
    PortfolioStrategyFactory,
)
from tests.mocks.backtester.data_preparer.mock_asset_matrix_preparer import (
    MockAssetMatrixPreparer,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioStrategyFactory(PortfolioStrategyFactory):
    def __init__(self):
        self.asset_matrix_preparer = MockAssetMatrixPreparer()
        self.logger = MockLoggable()
        self.strategy_logger = MockLoggable()
        super().__init__(
            asset_matrix_preparer=self.asset_matrix_preparer,
            logger=self.logger,
            strategy_logger=self.strategy_logger,
        )
        self.raise_exception = False
        self.return_empty = False

        class DummyPortfolioStrategy(BasePortfolioStrategy):
            def allocate(self, *args, **kwargs):
                return {}

        self.default_base_portfolio_strategy = DummyPortfolioStrategy(
            logger=self.strategy_logger,
        )
        self.base_portfolio_strategy = self.default_base_portfolio_strategy
        self.default_buffered_portfolio_strategy = BufferedPortfolioStrategy(
            strategy=self.default_base_portfolio_strategy,
            asset_matrix_preparer=self.asset_matrix_preparer,
            logger=self.strategy_logger,
        )
        self.buffered_portfolio_strategy = self.default_buffered_portfolio_strategy

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset(self):
        self.raise_exception = False
        self.return_empty = False
        self.base_portfolio_strategy = self.default_base_portfolio_strategy
        self.buffered_portfolio_strategy = self.default_buffered_portfolio_strategy

    def build_strategy(
        self, strategy_class: type[BasePortfolioStrategy], params: dict
    ) -> BasePortfolioStrategy | None:
        if self.raise_exception:
            raise Exception("Mocked exception in build_strategy")
        if self.return_empty:
            return None
        return self.base_portfolio_strategy

    def build_buffered_strategy(
        self, strategy_class: type[BasePortfolioStrategy], params: dict
    ) -> BufferedPortfolioStrategy | None:
        if self.raise_exception:
            raise Exception("Mocked exception in build_buffered_strategy")
        if self.return_empty:
            return None
        return self.buffered_portfolio_strategy
