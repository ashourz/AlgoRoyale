import asyncio
from typing import Any, Callable, Optional, Union

from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.application.utils.queued_async_update_object import (
    QueuedAsyncUpdateObject,
)
from algo_royale.backtester.column_names.data_ingest_columns import DataIngestColumns
from algo_royale.models.alpaca_market_data.alpaca_stream_bar import StreamBar
from algo_royale.models.alpaca_market_data.alpaca_stream_quote import StreamQuote


class StreamDataIngestObject(QueuedAsyncUpdateObject):
    """
    Represents a data ingest object for streaming data.
    This is used to process incoming market data and generate signals.
    """

    update_type = "UPDATE"

    def __init__(self, symbol: str, logger=None):
        """
        Initialize the StreamDataIngestObject.
        """
        self.symbol = symbol
        self.latest_quote: StreamQuote = None
        self.latest_bar: StreamBar = None
        self.get_set_lock = asyncio.Lock()
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
        self._pubsub = AsyncPubSub()
        super().__init__(logger=logger)

    def subscribe(
        self,
        callback: Callable[[dict, type], Any],  # callback receives (data, object_type)
        queue_size: int = 1,
    ) -> AsyncSubscriber:
        """
        Subscribe to an event type with a callback and optional filter function.
        """
        return self._pubsub.subscribe(
            event_type=self.update_type,
            callback=callback,
            queue_size=queue_size,
        )

    def unsubscribe(self, subscriber: AsyncSubscriber):
        """
        Unsubscribe a subscriber from the pubsub system.
        """
        self._pubsub.unsubscribe(subscriber)

    async def async_shutdown(self):
        """
        Shutdown the pubsub system and cancel all tasks.
        """
        await self._pubsub.async_shutdown()

    async def async_get_latest_quote(self) -> Optional[StreamQuote]:
        """
        Get the latest market quote.
        """
        async with self.get_set_lock:
            # Return a copy to avoid external modifications
            return self.latest_quote.model_copy() if self.latest_quote else None

    async def async_get_latest_bar(self) -> Optional[StreamBar]:
        """
        Get the latest market bar.
        """
        async with self.get_set_lock:
            # Return a copy to avoid external modifications
            return self.latest_bar.model_copy() if self.latest_bar else None

    def _set_type_hierarchy(self, hierarchy: dict):
        """
        Set the type hierarchy mapping: type -> priority (int).
        """
        self.type_hierarchy = {
            StreamBar: 2,
            StreamQuote: 1,
        }

    async def _update(self, obj: Union[StreamQuote, StreamBar]):
        """
        Queue an update object by its type.
        If a higher-priority type comes in, remove lower-priority pending updates.
        """
        async with self.get_set_lock:
            if isinstance(obj, StreamQuote):
                self._update_with_quote(obj)
            elif isinstance(obj, StreamBar):
                self._update_with_bar(obj)
            else:
                raise TypeError(
                    f"[StreamDataIngestObject: {self.symbol}] Unsupported object type: {type(obj)}"
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
            current_high_price = self.data[DataIngestColumns.HIGH_PRICE]
            current_low_price = self.data[DataIngestColumns.LOW_PRICE]
            new_high_price = (
                max(average_price, current_high_price)
                if average_price
                else current_high_price
            )
            new_low_price = (
                min(quote.ask_price, current_low_price)
                if average_price
                else current_low_price
            )

            last_bar_open = self.latest_bar.open_price if self.latest_bar else None
            last_bar_close = self.latest_bar.close_price if self.latest_bar else None
            self.data[DataIngestColumns.OPEN_PRICE] = (
                last_bar_close if last_bar_close else last_bar_open
            )
            self.data[DataIngestColumns.CLOSE_PRICE] = (
                average_price if average_price else last_bar_close
            )
            self.data[DataIngestColumns.HIGH_PRICE] = new_high_price
            self.data[DataIngestColumns.LOW_PRICE] = new_low_price
            self.data[DataIngestColumns.TIMESTAMP] = quote.timestamp
            self._pubsub.async_publish(
                event_type=self.update_type, data=self.data.copy()
            )

        except Exception as e:
            self.logger.error(
                f"[StreamDataIngestObject: {self.symbol}] Error _updating with quote: {e}"
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
            self._pubsub.async_publish(
                event_type=self.update_type, data=self.data.copy()
            )
        except Exception as e:
            self.logger.error(
                f"[StreamDataIngestObject: {self.symbol}] Error _updating with bar: {e}"
            )
