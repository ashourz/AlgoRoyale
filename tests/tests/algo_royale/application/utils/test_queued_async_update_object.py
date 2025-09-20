import asyncio

import pytest

from src.algo_royale.application.utils.queued_async_update_object import (
    QueuedAsyncUpdateObject,
)


class DummyObj:
    def __init__(self):
        self.value = 0

    async def update(self, v):
        self.value = v
        return v


from tests.mocks.mock_loggable import MockLoggable


class DummyQueuedAsyncUpdateObject(QueuedAsyncUpdateObject):
    def __init__(self, obj, logger=None):
        super().__init__(logger=logger)
        self.obj = obj

    def _type_hierarchy(self):
        return []

    async def _update(self, *args, **kwargs):
        return await self.obj.update(*args, **kwargs)


@pytest.mark.asyncio
class TestQueuedAsyncUpdateObject:
    def setup_method(self):
        self.obj = DummyObj()
        self.q = DummyQueuedAsyncUpdateObject(self.obj, logger=MockLoggable())

    @pytest.mark.asyncio
    async def test_enqueue_and_process_normal(self):
        await self.q.async_update(1)
        await self.q.async_update(2)
        # No explicit process_updates; async_update processes immediately
        assert self.obj.value == 2

    @pytest.mark.asyncio
    async def test_process_updates_exception(self):
        async def bad_update(v):
            raise Exception("fail")

        self.obj.update = bad_update
        # Should not raise, error is caught and logged
        await self.q.async_update(1)

    @pytest.mark.asyncio
    async def test_multiple_updates(self):
        for i in range(5):
            await self.q.async_update(i)
        assert self.obj.value == 4

    def test_queue_empty(self):
        # No is_empty or process_updates in the implementation; test basic update
        assert self.obj.value == 0
        asyncio.run(self.q.async_update(1))
        assert self.obj.value == 1
