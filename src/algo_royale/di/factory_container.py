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
from algo_royale.logging.logger_type import LoggerType


class FactoryContainer:
    def __init__(self, config, logger_container):
        self.config = config
        self.logger_container = logger_container

        self.signal_strategy_factory = SignalStrategyFactory(
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_FACTORY
            ),
            strategy_logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY
            ),
        )

        self.signal_strategy_combinator_factory = SignalStrategyCombinatorFactory(
            combinator_list_path=self.config["backtester_paths"][
                "signal_strategy_combinators"
            ],
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_COMBINATOR_FACTORY
            ),
        )

        self.signal_strategy_optimizer_factory = SignalStrategyOptimizerFactoryImpl(
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_OPTIMIZER_FACTORY
            ),
            strategy_logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY
            ),
        )

        self.portfolio_strategy_combinator_factory = PortfolioStrategyCombinatorFactory(
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

        self.portfolio_strategy_optimizer_factory = (
            PortfolioStrategyOptimizerFactoryImpl(
                logger=self.logger_container.logger(
                    logger_type=LoggerType.PORTFOLIO_STRATEGY_OPTIMIZER_FACTORY
                ),
                strategy_logger=self.logger_container.logger(
                    logger_type=LoggerType.PORTFOLIO_STRATEGY
                ),
            )
        )
