from algo_royale.application.utils.queued_async_update_object import (
    QueuedAsyncUpdateObject,
)


class QueuedAsyncSymbolList(QueuedAsyncUpdateObject):
    def _type_hierarchy(self):
        # No type hierarchy needed for symbol list, return empty dict
        return {}

    """
    Represents a queued async update object for a list of signal data payloads.
    This is used to process incoming signal data and generate signals for multiple symbols.
    """

    def __init__(self, symbols: set[str] = None, logger=None):
        super().__init__(logger=logger)
        self.symbols: set[str] = symbols or set()

    def _update(self, symbol: str):
        """
        Update the list of symbols.
        """
        self.symbols.add(symbol)
