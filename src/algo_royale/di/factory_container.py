from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer_factory import (
    PortfolioStrategyOptimizerFactoryImpl,
)
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    SignalStrategyOptimizerFactoryImpl,
)
from algo_royale.backtester.strategy_factory.portfolio.portfolio_strategy_combinator_factory import (
    PortfolioStrategyCombinatorFactory,
)
from algo_royale.backtester.strategy_factory.portfolio.portfolio_strategy_factory import (
    PortfolioStrategyFactory,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_combinator_factory import (
    SignalStrategyCombinatorFactory,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_factory import (
    SignalStrategyFactory,
)
from algo_royale.logging.logger_type import LoggerType


class FactoryContainer:
    def __init__(self, config, logger_container):
        self.config = config
        self.logger_container = logger_container

    @property
    def signal_strategy_factory(self) -> SignalStrategyFactory:
        return SignalStrategyFactory(
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_FACTORY
            ),
            strategy_logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY
            ),
        )

    @property
    def signal_strategy_combinator_factory(self) -> SignalStrategyCombinatorFactory:
        return SignalStrategyCombinatorFactory(
            combinator_list_path=self.config["backtester_paths"][
                "signal_strategy_combinators"
            ],
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_COMBINATOR_FACTORY
            ),
        )

    @property
    def signal_strategy_optimizer_factory(self) -> SignalStrategyOptimizerFactoryImpl:
        return SignalStrategyOptimizerFactoryImpl(
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_OPTIMIZER_FACTORY
            ),
            strategy_logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY
            ),
        )

    @property
    def portfolio_strategy_combinator_factory(
        self,
    ) -> PortfolioStrategyCombinatorFactory:
        return PortfolioStrategyCombinatorFactory(
            combinator_list_path=self.config["backtester_paths"][
                "portfolio_strategy_combinators"
            ],
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_STRATEGY_COMBINATOR_FACTORY
            ),
            strategy_logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_STRATEGY
            ),
        )

    @property
    def portfolio_strategy_optimizer_factory(
        self,
    ) -> PortfolioStrategyOptimizerFactoryImpl:
        return PortfolioStrategyOptimizerFactoryImpl(
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_STRATEGY_OPTIMIZER_FACTORY
            ),
            strategy_logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_STRATEGY
            ),
        )

    @property
    def asset_matrix_preparer(self) -> AssetMatrixPreparer:
        return AssetMatrixPreparer(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ASSET_MATRIX_PREPARER
            )
        )

    @property
    def portfolio_strategy_factory(self) -> PortfolioStrategyFactory:
        return PortfolioStrategyFactory(
            asset_matrix_preparer=self.asset_matrix_preparer,
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_STRATEGY_FACTORY
            ),
            strategy_logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_STRATEGY
            ),
        )
