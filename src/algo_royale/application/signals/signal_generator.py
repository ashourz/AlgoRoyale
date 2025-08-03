from algo_royale.application.strategies.strategy_registry import StrategyRegistry
from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.backtester.strategy.signal.combined_weighted_signal_strategy import (
    CombinedWeightedSignalStrategy,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_stream_quote import StreamQuote
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.services.market_data.stream_service import StreamService


class SignalGenerator:
    def __init__(
        self,
        symbol_manager: SymbolManager,
        stream_service: StreamService,
        strategy_registry: StrategyRegistry,
        logger: Loggable,
        is_live: bool = False,
    ):
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.stream_service = stream_service
        self.strategy_registry = strategy_registry
        self.is_live = is_live
        self.symbol_strategy_map: dict[str, CombinedWeightedSignalStrategy] = {}
        self.logger.info("SignalGenerator initialized.")

    async def start(self):
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            self.logger.info("Loading symbol strategies...")
            self._load_symbol_strategies()
            self.logger.info("Starting signal generation...")
            feed = DataFeed.SIP if self.is_live else DataFeed.IEX
            symbols = await self.symbol_manager.get_symbols()
            self.logger.info(
                f"Starting signal generation | feed: {feed} | symbols: {symbols}"
            )
            self.stream_service.start_stream(symbols=symbols, on_quote=self._onQuote)
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")

    def _load_symbol_strategies(self):
        """
        Load symbol strategies from the strategy registry.
        """
        try:
            for symbol in self.symbol_manager.get_symbols():
                self.logger.debug(f"Loading strategies for symbol: {symbol}")
                self.symbol_strategy_map[symbol] = (
                    self.strategy_registry.get_combined_weighted_signal_strategy(
                        symbol=symbol
                    )
                )
            self.logger.info("Symbol strategies loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading symbol strategies: {e}")

    def _onQuote(self, quote: StreamQuote):
        """
        Handle incoming market quotes and generate signals.

        :param quote: The market quote data.
        """
        try:
            self.logger.info(f"Received quote: {quote}")
            signal = self._generate_signal(quote)
            self.logger.info(f"Generated signal: {signal}")
            # Here you would typically send the signal to a trading engine or strategy
        except Exception as e:
            self.logger.error(f"Error processing quote: {e}")

    def _generate_signals(self, quote: StreamQuote) -> dict:
        """
        Generate trading signals based on the incoming quote and loaded strategies.

        :param quote: The market quote data.
        :return: A dictionary containing the generated signals.
        """
        try:
            symbol = quote.symbol
            if symbol not in self.symbol_strategy_map:
                self.logger.warning(f"No strategy found for symbol: {symbol}")
                return None

            strategy = self.symbol_strategy_map[symbol]
            ##TODO: map quote to the strategy's expected input format
            signals = strategy.generate_signals(quote)
            return signals
        except Exception as e:
            self.logger.error(f"Error generating signal for {quote.symbol}: {e}")
            return None

    def stop(self):
        """
        Stop the signal generation service.
        """
        try:
            self.logger.info("Stopping signal generation...")
            self.stream_service.stop_stream()
            self.logger.info("Signal generation stopped.")
            self.symbol_strategy_map.clear()
            self.logger.info("Symbol strategy map cleared.")
        except Exception as e:
            self.logger.error(f"Error stopping signal generation: {e}")
