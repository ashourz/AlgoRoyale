from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.utils.queued_async_update_object import (
    QueuedAsyncUpdateObject,
)


class QueuedAsyncSymbolHold(QueuedAsyncUpdateObject):
    def _type_hierarchy(self):
        # No type hierarchy needed for symbol hold, return empty dict
        return {}

    """
    Represents a queued async update object for symbol holds.
    This is used to process incoming symbol hold updates.
    """

    def __init__(self, logger=None):
        super().__init__(logger=logger)
        self.status: SymbolHoldStatus = SymbolHoldStatus.CLOSED_FOR_DAY

    def _update(self, status: SymbolHoldStatus):
        """
        Update the list of symbols.
        """
        self.status = status
