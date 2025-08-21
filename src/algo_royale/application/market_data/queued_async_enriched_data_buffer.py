import asyncio

import pandas as pd

from algo_royale.application.utils.queued_async_update_object import (
    QueuedAsyncUpdateObject,
)
from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer
from algo_royale.logging.loggable import Loggable


class QueuedAsyncEnrichedDataBuffer(QueuedAsyncUpdateObject):
    def __init__(
        self, symbol: str, feature_engineer: FeatureEngineer, logger: Loggable
    ):
        super().__init__()
        self.symbol = symbol
        self.get_set_lock = asyncio.Lock()
        self.feature_engineer = feature_engineer
        self.max_lookback = self.feature_engineer.compute_max_lookback()
        self.buffer = pd.DataFrame()
        self.logger = logger

    async def _update(self, data: pd.Series):
        try:
            async with self.get_set_lock:
                # Ensure the buffer is initialized
                if self.buffer.empty:
                    self.buffer = pd.DataFrame(columns=data.index)
                self.logger.debug(
                    f"Updating buffer for {self.symbol} with data: {data}"
                )
                self.buffer = pd.concat(
                    [self.buffer, data.to_frame().T], ignore_index=True
                )
                if len(self.buffer) > self.max_lookback:
                    self.buffer = self.buffer.iloc[-self.max_lookback :]
                updated_row = self.feature_engineer.enrich_data(self.buffer)
                # Update the buffer with the enriched data
                self.buffer.iloc[-1] = updated_row
        except Exception as e:
            self.logger.error(f"Error updating buffer for {self.symbol}: {e}")

    async def async_get_latest_enriched_data(self) -> pd.Series | None:
        async with self.get_set_lock:
            if not self.buffer.empty:
                return self.buffer.iloc[-1]
            self.logger.warning(f"No enriched data found for {self.symbol}")
            return None

    async def async_clear_buffer(self):
        async with self.get_set_lock:
            self.buffer = pd.DataFrame()
            self.logger.info(f"Cleared buffer for {self.symbol}")
