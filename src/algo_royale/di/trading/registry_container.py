from dependency_injector import containers, providers

from algo_royale.application.strategies.portfolio_strategy_registry import (
    PortfolioStrategyRegistry,
)
from algo_royale.application.strategies.signal_strategy_registry import (
    SignalStrategyRegistry,
)
from algo_royale.di.factory_container import FactoryContainer
from algo_royale.di.ledger_service_container import LedgerServiceContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.logging.logger_type import LoggerType


class RegistryContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    factory_container: FactoryContainer = providers.DependenciesContainer()
    stage_data_container: StageDataContainer = providers.DependenciesContainer()
    ledger_service_container: LedgerServiceContainer = providers.DependenciesContainer()
    logger_container: LoggerContainer = providers.DependenciesContainer()

    signal_strategy_registry = providers.Singleton(
        SignalStrategyRegistry,
        symbol_service=ledger_service_container.symbol_service,
        stage_data_manager=stage_data_container.stage_data_manager,
        evaluation_json_filename=config.backtester.signal.filenames.signal_evaluation_json_filename,
        viable_strategies_path=config.trading.paths.viable_signal_strategies_path,
        signal_strategy_factory=factory_container.signal_strategy_factory,
        logger=logger_container.logger(logger_type=LoggerType.SIGNAL_STRATEGY_REGISTRY),
        combined_buy_threshold=config.trading.combined_buy_threshold,
        combined_sell_threshold=config.trading.combined_sell_threshold,
    )

    portfolio_strategy_registry = providers.Singleton(
        PortfolioStrategyRegistry,
        symbol_service=ledger_service_container.symbol_service,
        stage_data_manager=stage_data_container.stage_data_manager,
        evaluation_json_filename=config.backtester.portfolio.filenames.portfolio_strategy_evaluation_json_filename,
        viable_strategies_path=config.trading.paths.viable_portfolio_strategies_path,
        portfolio_strategy_factory=factory_container.portfolio_strategy_factory,
        logger=logger_container.logger(
            logger_type=LoggerType.PORTFOLIO_STRATEGY_REGISTRY
        ),
    )
