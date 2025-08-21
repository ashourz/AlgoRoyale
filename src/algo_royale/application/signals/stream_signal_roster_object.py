from typing import Any, Callable

from algo_royale.application.signals.queued_async_data_payload import (
    QueuedAsyncSignalDataPayload,
)
from algo_royale.application.signals.queued_async_symbol_list import (
    QueuedAsyncSymbolList,
)
from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber


class StreamSignalRosterObject:
    """
    This class manages the roster of signals for a specific symbol.
    """

    update_type = "UPDATE"

    def __init__(self, initial_symbols: list[str], logger=None):
        """
        Initialize the StreamSignalRosterObject.
        """
        self.logger = logger
        self._pubsub = AsyncPubSub()
        self._queued_symbols_list = QueuedAsyncSymbolList(symbols=initial_symbols)
        self._initialize_signal_data(self, symbols=initial_symbols)

    def _initialize_signal_data(self, symbols: list[str]):
        """
        Initialize the signal data structure for the given symbols.
        This creates a pubsub queue for each symbol to handle signal updates.
        """
        for symbol in symbols:
            self._get_signal_payload_queue(symbol)

    def _get_queued_async_signal_data_payload_name(self, symbol: str) -> str:
        """
        Get the name of the pubsub queue for a specific symbol.
        """
        return f"signal_data_payload_{symbol}"

    def _get_signal_payload_queue(self, symbol: str) -> QueuedAsyncSignalDataPayload:
        """
        Get the signal payload queue for a specific symbol.
        If it doesn't exist, create a new one.
        """
        queue_name = self._get_queued_async_signal_data_payload_name(symbol)
        value = getattr(self, queue_name, None)
        if not isinstance(value, QueuedAsyncSignalDataPayload):
            self.logger.warning(
                f"No queued async signal data payload found for symbol: {symbol}. Creating new one."
            )
            setattr(self, queue_name, QueuedAsyncSignalDataPayload(symbol))
            value = getattr(self, queue_name)
        return value

    async def _async_get_signal_data_payload(self, symbol: str) -> SignalDataPayload:
        """
        Get the signal payload for a specific symbol.
        """
        queue = self._get_signal_payload_queue(symbol)
        # Now get the payload
        return await queue.async_get_payload()

    async def _async_update_queued_symbols_list(self, symbol: str):
        """
        Update the list of symbols in the queued async symbol list.
        """
        if symbol not in self._queued_symbols_list.symbols:
            await self._queued_symbols_list.async_update(symbol)

    async def _async_set_signal_data_payload(
        self, symbol: str, payload: SignalDataPayload
    ):
        """
        Set the signal payload for a specific symbol.
        """
        queue = self._get_signal_payload_queue(symbol)
        # Now set the payload
        await queue.async_set_payload(payload)

    async def async_set_signal_data_payload(
        self, symbol: str, payload: SignalDataPayload
    ):
        """Set the signal data payload for a specific symbol.
        This will update the queued symbols list and the signal data payload.
        """
        await self._async_update_queued_symbols_list(symbol)
        await self._async_set_signal_data_payload(symbol, payload)
        await self._async_publish_roster_update()

    async def _async_get_signal_data_roster(
        self, symbols: list[str]
    ) -> dict[str, SignalDataPayload]:
        """
        Get the signal data payloads for a list of symbols.
        Returns a dictionary mapping symbol to SignalDataPayload.
        """
        payloads = {}
        for symbol in symbols:
            payload = await self._async_get_signal_data_payload(symbol)
            payloads[symbol] = payload.copy()
        return payloads

    async def _async_publish_roster_update(self):
        """Publish the current roster of signal data payloads.
        This will notify all subscribers of the latest state.
        """
        symbols = self._queued_symbols_list.symbols
        roster = await self._async_get_signal_data_roster(symbols=symbols)
        await self._pubsub.async_publish(self.update_type, roster)

    def subscribe(
        self,
        callback: Callable[
            [dict[str, SignalDataPayload], type], Any
        ],  # callback receives (data, object_type)
        queue_size: int = 1,
    ) -> AsyncSubscriber:
        """Subscribe to updates with a callback."""
        return self._pubsub.subscribe(
            event_type=self.update_type, callback=callback, queue_size=queue_size
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
