import asyncio

from algo_royale.application.orders.equity_order_enums import EquityOrderSide
from algo_royale.application.orders.equity_order_types import (
    EquityMarketNotionalOrder,
    EquityMarketQtyOrder,
)
from algo_royale.application.signals.signal_generator import SignalGenerator
from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.strategies.portfolio_strategy_registry import (
    PortfolioStrategyRegistry,
)
from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enums.signal_type import SignalType
from algo_royale.backtester.strategy.portfolio.buffered_components.buffered_portfolio_strategy import (
    BufferedPortfolioStrategy,
)
from algo_royale.events.async_pubsub import AsyncPubSub
from algo_royale.logging.loggable import Loggable


class OrderGenerator:
    order_event_type = "ORDER_GENERATED"

    def __init__(
        self,
        symbol_manager: SymbolManager,
        signal_generator: SignalGenerator,
        portfolio_strategy_registry: PortfolioStrategyRegistry,
        logger: Loggable,
    ):
        """
        Initialize the OrderGenerator with a trading symbol and an optional logger.

        Args:
            signal_generator (SignalGenerator): The signal generator instance.
            logger (Loggable): Logger for logging events and errors.
        """
        self.logger = logger
        self.symbol_manager = symbol_manager
        # SIGNAL GENERATOR
        self.signal_generator = signal_generator
        # PORTFOLIO STRATEGY REGISTRY
        self.portfolio_strategy_registry = portfolio_strategy_registry
        # ORDERS
        self.order_lock: asyncio.Lock = asyncio.Lock()
        self.pubsub_orders_map: dict[str, AsyncPubSub] = {}
        self.portfolio_strategy: BufferedPortfolioStrategy = None
        self.logger.info("OrderGenerator initialized.")

    async def async_start(self):
        """
        Start the order generation process.
        """
        try:
            symbols = await self.symbol_manager.async_get_symbols()
            self.portfolio_strategy = (
                self.portfolio_strategy_registry.get_buffered_portfolio_strategy(
                    symbols=symbols
                )
            )
            self.logger.info("Subscribing to streams...")
            self._subscribe_to_roster_stream()
            self.logger.info("Starting signal generation...")
            await self.signal_generator.async_start()
            self.logger.info("Starting order generation...")
        except Exception as e:
            self.logger.error(f"Error starting order generation: {e}")

    def _subscribe_to_roster_stream(self):
        """Subscribe to the signal roster stream to receive updates."""
        try:
            self.logger.info("Subscribing to signal roster stream...")
            async_subscriber = self.signal_generator.subscribe_to_signals(
                callback=lambda roster: self._async_generate_orders(roster=roster),
            )
            self.signal_roster_subscriber = async_subscriber
        except Exception as e:
            self.logger.error(f"Error subscribing to signal stream: {e}")

    async def _async_generate_orders(self, roster: dict[str, SignalDataPayload]):
        """
        Generate orders based on the provided signal roster.
        """
        try:
            async with self.order_lock:
                # generate order
                self._generate_orders(roster=roster)
        except Exception as e:
            self.logger.error(f"Error generating order: {e}")
            return

    def _generate_orders(self, roster: dict[str, SignalDataPayload]):
        """
        Generate trading orders based on the provided signal roster.
        """
        try:
            if not self.portfolio_strategy:
                self.logger.error("Portfolio strategy is not initialized.")
                return

            # Generate weights based on the signal roster
            df = self.portfolio_strategy.update(roster=roster)
            if df is None:
                self.logger.warning("No valid data to generate orders.")
                return
            weights = df.get("weights", {})
            if not weights:
                self.logger.warning("No weights generated for the portfolio.")
                return

            orders = []
            for symbol, signalDataPayload in roster.items():
                entry_signal = signalDataPayload.signals.get(
                    SignalStrategyColumns.ENTRY_SIGNAL
                )
                exit_signal = signalDataPayload.signals.get(
                    SignalStrategyColumns.EXIT_SIGNAL
                )
                weight = weights.get(symbol, None)
                # Handle entry signal
                if entry_signal == SignalType.BUY.value:
                    # Generate buy order
                    if weight is not None:
                        order = self._generate_buy_order(
                            symbol, weight, signalDataPayload.price_data
                        )
                        orders.append(order)
                # Handle exit signal
                elif exit_signal == SignalType.SELL.value:
                    if weight is not None:
                        order = self._generate_sell_order(
                            symbol, weight, signalDataPayload.price_data
                        )
                        orders.append(order)
            if orders:
                # Publish all generated orders
                for order in orders:
                    self._publish_order_event(order)
        except Exception as e:
            self.logger.error(f"Error generating orders: {e}")

    def _generate_buy_order(self, symbol: str, weight: float, price_data: dict):
        """
        Generate a buy order for the given symbol with the specified weight.
        """
        funds_at_open = self.ledger.get_funds_at_open()
        available_funds = self.ledger.get_available_funds()
        notional_value = min(funds_at_open * weight, available_funds)
        order = EquityMarketNotionalOrder(
            symbol=symbol,
            action=EquityOrderSide.BUY,
            notional=notional_value,
        )
        self.logger.info(f"Generated buy order: {order}")
        ##TODO: publish order event
        self._publish_order_event(order)

    def _generate_sell_order(self, symbol: str, weight: float, price_data: dict):
        """
        Generate a sell order for the given symbol with the specified weight.
        """
        # Get current position
        ##TODO: get this position from ledger
        current_position = self.ledger.get_position(symbol)
        order = EquityMarketQtyOrder(
            symbol=symbol, action=EquityOrderSide.SELL, quantity=current_position
        )
        self.logger.info(f"Generated sell order: {order}")
        ##TODO: publish order event
        self._publish_order_event(order)
