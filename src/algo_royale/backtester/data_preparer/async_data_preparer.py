import logging

from algo_royale.logging.logger_singleton import mockLogger


class AsyncDataPreparer:
    def __init__(self, logger: logging.Logger):
        """
        Initialize the AsyncDataPreparer with a logger.
        """
        self.logger: logging.Logger = logger

    async def normalize_stream(self, iterator_factory):
        iterator = iterator_factory()
        if not hasattr(iterator, "__aiter__"):
            self.logger.error(f"Expected async iterator, got {type(iterator)}")
            raise TypeError(f"Expected async iterator, got {type(iterator)}")
        try:
            async for df in iterator:
                yield df
        finally:
            if hasattr(iterator, "aclose"):
                await iterator.aclose()


def mockAsyncDataPreparer() -> AsyncDataPreparer:
    """Creates a mock AsyncDataPreparer for testing purposes."""

    logger: logging.Logger = mockLogger()
    return AsyncDataPreparer(logger=logger)
