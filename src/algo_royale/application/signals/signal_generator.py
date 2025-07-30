from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_stream_quote import StreamQuote
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.services.market_data.stream_service import StreamService


class SignalGenerator:
    def __init__(
        self,
        symbol_manager: SymbolManager,
        stream_service: StreamService,
        logger: Loggable,
        is_live: bool = False,
    ):
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.stream_service = stream_service

    def start(self):
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            self.logger.info("Starting signal generation...")
            feed = DataFeed.SIP if self.is_live else DataFeed.IEX
            symbols = self.symbol_manager.get_symbols()
            self.logger.info(
                f"Starting signal generation | feed: {feed} | symbols: {symbols}"
            )
            self.stream_service.start_stream(symbols=symbols, on_quote=self._onQuote)
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")

    def _onQuote(self, quote: StreamQuote):
        """
        Handle incoming market quotes and generate signals.

        :param quote: The market quote data.
        """
        try:
            self.logger.info(f"Received quote: {quote}")
            signal = self.generate_signal(quote)
            self.logger.info(f"Generated signal: {signal}")
            # Here you would typically send the signal to a trading engine or strategy
        except Exception as e:
            self.logger.error(f"Error processing quote: {e}")
