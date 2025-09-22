from algo_royale.application.strategies.portfolio_strategy_registry import (
    PortfolioStrategyRegistry,
)
from algo_royale.application.strategies.signal_strategy_registry import (
    SignalStrategyRegistry,
)
from algo_royale.logging.logger_type import LoggerType


class RegistryContainer:
    def __init__(
        self,
        config,
        factory_container,
        stage_data_container,
        ledger_service_container,
        logger_container,
    ):
        self.config = config
        self.factory_container = factory_container
        self.stage_data_container = stage_data_container
        self.ledger_service_container = ledger_service_container
        self.logger_container = logger_container

        self.signal_strategy_registry = SignalStrategyRegistry(
            symbol_service=self.ledger_service_container.symbol_service,
            stage_data_manager=self.stage_data_container.stage_data_manager,
            evaluation_json_filename=self.config["backtester_signal_filenames"][
                "signal_evaluation_json_filename"
            ],
            viable_strategies_path=self.config["trading_paths"][
                "viable_signal_strategies_path"
            ],
            signal_strategy_factory=self.factory_container.signal_strategy_factory,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_REGISTRY
            ),
            combined_buy_threshold=float(
                self.config["trading"]["combined_buy_threshold"]
            ),
            combined_sell_threshold=float(
                self.config["trading"]["combined_sell_threshold"]
            ),
        )

        self.portfolio_strategy_registry = PortfolioStrategyRegistry(
            symbol_service=self.ledger_service_container.symbol_service,
            stage_data_manager=self.stage_data_container.stage_data_manager,
            evaluation_json_filename=self.config["backtester_portfolio_filenames"][
                "portfolio_strategy_evaluation_json_filename"
            ],
            viable_strategies_path=self.config["trading_paths"][
                "viable_portfolio_strategies_path"
            ],
            portfolio_strategy_factory=self.factory_container.portfolio_strategy_combinator_factory,
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_STRATEGY_REGISTRY
            ),
        )
