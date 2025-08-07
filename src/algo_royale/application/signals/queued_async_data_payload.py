import asyncio

from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.utils.queued_async_update_object import (
    QueuedAsyncUpdateObject,
)


class QueuedAsyncSignalDataPayload(QueuedAsyncUpdateObject):
    """
    Represents a queued async update object for signal data payloads.
    This is used to process incoming signal data and generate signals.
    """

    def __init__(self, symbol: str, get_set_timeout: float = None, logger=None):
        self.symbol = symbol
        self.get_set_lock = asyncio.Lock()
        self.data: SignalDataPayload | None = None
        self.get_set_timeout = get_set_timeout
        super().__init__(logger=logger)

    async def async_set_payload(self, payload: SignalDataPayload):
        """
        Set the signal data payload.
        """
        try:
            await asyncio.wait_for(
                self._set_payload_locked(payload), self.get_set_timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timed out setting payload for {self.symbol}")

    async def _set_payload_locked(self, payload: SignalDataPayload):
        """
        Set the signal data payload.
        """
        async with self.get_set_lock:
            self.data = payload
            await self.async_update(self, payload)

    async def async_get_payload(self) -> SignalDataPayload | None:
        """
        Get the signal data payload.
        """
        try:
            return await asyncio.wait_for(
                self._get_payload_locked(), self.get_set_timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timed out getting payload for {self.symbol}")

    async def _get_payload_locked(self) -> SignalDataPayload | None:
        """
        Get the signal data payload.
        """
        async with self.get_set_lock:
            return self.data

    async def _update(self, payload: SignalDataPayload):
        """
        Update the signal data payload.
        """
        if not isinstance(payload, SignalDataPayload):
            raise ValueError("Payload must be an instance of SignalDataPayload")
        self.data = payload
