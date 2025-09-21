from dependency_injector import containers, providers

from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer_factory import (
    PortfolioStrategyOptimizerFactoryImpl,
)
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    SignalStrategyOptimizerFactoryImpl,
)
from algo_royale.backtester.strategy_factory.portfolio.portfolio_strategy_combinator_factory import (
    PortfolioStrategyCombinatorFactory,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_combinator_factory import (
    SignalStrategyCombinatorFactory,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_factory import (
    SignalStrategyFactory,
)
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType


class FactoryContainer(containers.DeclarativeContainer):
    """Factory Container"""

    config = providers.Configuration()
    logger_container: LoggerContainer = providers.DependenciesContainer()

    signal_strategy_factory = providers.Singleton(
        SignalStrategyFactory,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.SIGNAL_STRATEGY_FACTORY
        ),
        strategy_logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.SIGNAL_STRATEGY
        ),
    )

    signal_strategy_combinator_factory = providers.Singleton(
        SignalStrategyCombinatorFactory,
        combinator_list_path=config.backtester.paths.signal_strategy_combinators,
        logger=providers.Factory(
            logger_container.logger,
            logger_type=LoggerType.SIGNAL_STRATEGY_COMBINATOR_FACTORY,
        ),
    )

    signal_strategy_optimizer_factory = providers.Singleton(
        SignalStrategyOptimizerFactoryImpl,
        logger=providers.Factory(
            logger_container.logger,
            logger_type=LoggerType.SIGNAL_STRATEGY_OPTIMIZER_FACTORY,
        ),
        strategy_logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.SIGNAL_STRATEGY
        ),
    )

    portfolio_strategy_combinator_factory = providers.Singleton(
        PortfolioStrategyCombinatorFactory,
        combinator_list_path=config.backtester.paths.portfolio_strategy_combinators,
        logger=providers.Factory(
            logger_container.logger,
            logger_type=LoggerType.PORTFOLIO_STRATEGY_COMBINATOR_FACTORY,
        ),
        strategy_logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.PORTFOLIO_STRATEGY
        ),
    )

    portfolio_strategy_optimizer_factory = providers.Singleton(
        PortfolioStrategyOptimizerFactoryImpl,
        logger=providers.Factory(
            logger_container.logger,
            logger_type=LoggerType.PORTFOLIO_STRATEGY_OPTIMIZER_FACTORY,
        ),
        strategy_logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.PORTFOLIO_STRATEGY
        ),
    )
