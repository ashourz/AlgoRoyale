from dependency_injector import containers, providers

from algo_royale.application.market_data.market_data_enriched_streamer import (
    MarketDataEnrichedStreamer,
)
from algo_royale.application.market_data.market_data_raw_streamer import (
    MarketDataRawStreamer,
)
from algo_royale.application.orders.order_generator import OrderGenerator
from algo_royale.application.signals.signal_generator import SignalGenerator
from algo_royale.application.symbols.symbol_hold_tracker import SymbolHoldTracker
from algo_royale.di.adapter.adapter_container import AdapterContainer
from algo_royale.di.feature_engineering_container import FeatureEngineeringContainer
from algo_royale.di.ledger_service_container import LedgerServiceContainer
from algo_royale.di.repo.repo_container import RepoContainer
from algo_royale.di.trading.registry_container import RegistryContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.order_event_service import OrderEventService
from algo_royale.services.order_generator_service import OrderGeneratorService
from algo_royale.services.symbol_hold_service import SymbolHoldService
from algo_royale.services.symbol_service import SymbolService


class OrderGeneratorServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    adapter_container: AdapterContainer = providers.DependenciesContainer()
    repo_container: RepoContainer = providers.DependenciesContainer()
    feature_engineering_container: FeatureEngineeringContainer = (
        providers.DependenciesContainer()
    )
    ledger_service_container: LedgerServiceContainer = providers.DependenciesContainer()
    registry_container: RegistryContainer = providers.DependenciesContainer()
    logger_container = providers.DependenciesContainer()

    market_data_streamer = providers.Singleton(
        MarketDataRawStreamer,
        stream_adapter=adapter_container.market_data_stream_adapter,
        logger=logger_container.logger(logger_type=LoggerType.MARKET_DATA_RAW_STREAMER),
        is_live=config.environment.is_live(),
    )

    enriched_data_streamer = providers.Singleton(
        MarketDataEnrichedStreamer,
        feature_engineer=feature_engineering_container.feature_engineer,
        market_data_streamer=market_data_streamer,
        logger=logger_container.logger(
            logger_type=LoggerType.MARKET_DATA_ENRICHED_STREAMER
        ),
    )

    signal_generator = providers.Singleton(
        SignalGenerator,
        enriched_data_streamer=enriched_data_streamer,
        strategy_registry=registry_container.signal_strategy_registry,
        logger=logger_container.logger(logger_type=LoggerType.SIGNAL_GENERATOR),
    )

    order_generator = providers.Singleton(
        OrderGenerator,
        signal_generator=signal_generator,
        portfolio_strategy_registry=registry_container.portfolio_strategy_registry,
        logger=logger_container.logger(logger_type=LoggerType.ORDER_GENERATOR),
    )

    symbol_service = providers.Singleton(
        SymbolService,
        watchlist_repo=repo_container.watchlist_repo,
        positions_service=ledger_service_container.positions_service,
        logger=logger_container.logger(logger_type=LoggerType.SYMBOL_SERVICE),
    )

    order_event_service = providers.Singleton(
        OrderEventService,
        order_stream_adapter=adapter_container.order_stream_adapter,
        logger=logger_container.logger(logger_type=LoggerType.ORDER_EVENT_SERVICE),
    )

    symbol_hold_tracker = providers.Factory(
        SymbolHoldTracker,
        logger=logger_container.logger(logger_type=LoggerType.SYMBOL_HOLD_TRACKER),
    )

    symbol_hold_service = providers.Singleton(
        SymbolHoldService,
        symbol_service=symbol_service,
        symbol_hold_tracker=symbol_hold_tracker,
        order_service=ledger_service_container.order_service,
        order_event_service=order_event_service,
        positions_service=ledger_service_container.positions_service,
        trades_service=ledger_service_container.trades_service,
        logger=logger_container.logger(logger_type=LoggerType.SYMBOL_HOLD_SERVICE),
        post_fill_delay_seconds=config.trading.post_fill_delay_seconds,
    )

    order_generator_service = providers.Singleton(
        OrderGeneratorService,
        order_generator=order_generator,
        symbol_hold_service=symbol_hold_service,
        logger=logger_container.logger(logger_type=LoggerType.ORDER_GENERATOR_SERVICE),
    )
