from algo_royale.application.market_data.market_data_enriched_streamer import (
    MarketDataEnrichedStreamer,
)
from algo_royale.application.market_data.market_data_raw_streamer import (
    MarketDataRawStreamer,
)
from algo_royale.application.orders.order_generator import OrderGenerator
from algo_royale.application.signals.signal_generator import SignalGenerator
from algo_royale.application.symbols.symbol_hold_tracker import SymbolHoldTracker
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.order_event_service import OrderEventService
from algo_royale.services.order_generator_service import OrderGeneratorService
from algo_royale.services.symbol_hold_service import SymbolHoldService
from algo_royale.services.symbol_service import SymbolService


class OrderGeneratorServiceContainer:
    def __init__(
        self,
        config,
        adapter_container,
        repo_container,
        feature_engineering_container,
        ledger_service_container,
        registry_container,
        logger_container,
    ):
        self.config = config
        self.adapter_container = adapter_container
        self.repo_container = repo_container
        self.feature_engineering_container = feature_engineering_container
        self.ledger_service_container = ledger_service_container
        self.registry_container = registry_container
        self.logger_container = logger_container

        self.market_data_streamer = MarketDataRawStreamer(
            stream_adapter=self.adapter_container.stream_adapter,
            logger=self.logger_container.logger(
                logger_type=LoggerType.MARKET_DATA_RAW_STREAMER
            ),
            is_live=self.config["environment"]["is_live"],
        )

        self.enriched_data_streamer = MarketDataEnrichedStreamer(
            feature_engineer=self.feature_engineering_container.feature_engineer,
            market_data_streamer=self.market_data_streamer,
            logger=self.logger_container.logger(
                logger_type=LoggerType.MARKET_DATA_ENRICHED_STREAMER
            ),
        )

        self.signal_generator = SignalGenerator(
            enriched_data_streamer=self.enriched_data_streamer,
            strategy_registry=self.registry_container.signal_strategy_registry,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_GENERATOR
            ),
        )

        self.order_generator = OrderGenerator(
            signal_generator=self.signal_generator,
            portfolio_strategy_registry=self.registry_container.portfolio_strategy_registry,
            logger=self.logger_container.logger(logger_type=LoggerType.ORDER_GENERATOR),
        )

        self.symbol_service = SymbolService(
            watchlist_repo=self.repo_container.watchlist_repo(),
            positions_service=self.ledger_service_container.positions_service,
            logger=self.logger_container.logger(logger_type=LoggerType.SYMBOL_SERVICE),
        )

        self.order_event_service = OrderEventService(
            order_stream_adapter=self.adapter_container.order_stream_adapter,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ORDER_EVENT_SERVICE
            ),
        )

        self.symbol_hold_tracker = SymbolHoldTracker(
            logger=self.logger_container.logger(
                logger_type=LoggerType.SYMBOL_HOLD_TRACKER
            ),
        )

        self.symbol_hold_service = SymbolHoldService(
            symbol_service=self.symbol_service,
            symbol_hold_tracker=self.symbol_hold_tracker,
            order_service=self.ledger_service_container.order_service,
            order_event_service=self.order_event_service,
            positions_service=self.ledger_service_container.positions_service,
            trades_service=self.ledger_service_container.trades_service,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SYMBOL_HOLD_SERVICE
            ),
            post_fill_delay_seconds=self.config["trading"]["post_fill_delay_seconds"],
        )

        self.order_generator_service = OrderGeneratorService(
            order_generator=self.order_generator,
            symbol_hold_service=self.symbol_hold_service,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ORDER_GENERATOR_SERVICE
            ),
        )
