import asyncio

from algo_royale.backtester.column_names.data_ingest_columns import DataIngestColumns
from algo_royale.models.alpaca_market_data.alpaca_stream_bar import StreamBar
from algo_royale.models.alpaca_market_data.alpaca_stream_quote import StreamQuote


class StreamDataIngestObject:
    """
    Represents a data ingest object for streaming data.
    This is used to process incoming market data and generate signals.
    """

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.latest_quote: StreamQuote = None
        self.pending_quote = None
        self.latest_bar: StreamBar = None
        self.pending_bar = None
        self.lock = asyncio.Lock()
        self.data: dict = {
            DataIngestColumns.PRICE: None,
            DataIngestColumns.TIMESTAMP: None,
            DataIngestColumns.OPEN_PRICE: None,
            DataIngestColumns.HIGH_PRICE: None,
            DataIngestColumns.LOW_PRICE: None,
            DataIngestColumns.CLOSE_PRICE: None,
            DataIngestColumns.VOLUME: None,
            DataIngestColumns.NUM_TRADES: None,
            DataIngestColumns.VOLUME_WEIGHTED_PRICE: None,
        }

    async def async_get_data(self) -> dict:
        """
        Returns the data dictionary containing the data for this symbol.
        """
        try:
            async with self.lock:
                if not self.data:
                    return None
                # Confirm all columns are present
                for column in DataIngestColumns:
                    if column not in self.data:
                        return None
                return self.data
        except Exception as e:
            self.logger.error(
                f"[StreamDataIngestObject: {self.symbol}] Error getting data: {e}"
            )

    def _update_with_quote(self, quote: StreamQuote):
        """
        Update the data with a new market quote.
        """
        try:
            self.latest_quote = quote
            average_price = (
                (quote.ask_price + quote.bid_price) / 2
                if quote.ask_price and quote.bid_price
                else None
            )
            if average_price is not None:
                self.data[DataIngestColumns.PRICE] = average_price
            self.data[DataIngestColumns.TIMESTAMP] = quote.timestamp
        except Exception as e:
            self.logger.error(
                f"[StreamDataIngestObject: {self.symbol}] Error _updating with quote: {e}"
            )

    async def async_update_with_quote(self, quote: StreamQuote):
        """
        Update the data with a new market quote.
        """
        try:
            if self.lock.locked():
                self.pending_quote = quote
            else:
                async with self.lock:
                    self._update_with_quote(quote)

                    if self.pending_bar:
                        self.pending_quote = None
                        pending_bar = self.pending_bar
                        self.pending_bar = None
                        self._update_with_bar(pending_bar)
                    elif self.pending_quote:
                        pending_quote = self.pending_quote
                        self.pending_quote = None
                        self._update_with_quote(pending_quote)
        except Exception as e:
            self.logger.error(
                f"[StreamDataIngestObject: {self.symbol}] Error updating with quote: {e}"
            )

    def _update_with_bar(self, bar: StreamBar):
        """
        Update the data with a new market bar.
        """
        try:
            self.latest_bar = bar
            self.data[DataIngestColumns.TIMESTAMP] = bar.closing_epoch
            self.data[DataIngestColumns.OPEN_PRICE] = bar.open_price
            self.data[DataIngestColumns.HIGH_PRICE] = bar.high_price
            self.data[DataIngestColumns.LOW_PRICE] = bar.low_price
            self.data[DataIngestColumns.CLOSE_PRICE] = bar.close_price
            self.data[DataIngestColumns.VOLUME] = bar.volume
            self.data[DataIngestColumns.NUM_TRADES] = bar.num_trades
            self.data[DataIngestColumns.VOLUME_WEIGHTED_PRICE] = (
                bar.volume_weighted_price
            )
        except Exception as e:
            self.logger.error(
                f"[StreamDataIngestObject: {self.symbol}] Error _updating with bar: {e}"
            )

    async def async_update_with_bar(self, bar: StreamBar):
        """
        Update the data with a new market bar.
        """
        try:
            if self.lock.locked():
                self.pending_bar = bar
            else:
                async with self.lock:
                    self._update_with_bar(bar)
                    if self.pending_bar:
                        pending_bar = self.pending_bar
                        self.pending_bar = None
                        self._update_with_bar(pending_bar)
        except Exception as e:
            self.logger.error(
                f"[StreamDataIngestObject: {self.symbol}] Error updating with bar: {e}"
            )
