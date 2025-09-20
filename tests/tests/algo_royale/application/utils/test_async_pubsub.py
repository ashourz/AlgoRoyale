import asyncio

import pytest

from src.algo_royale.application.utils.async_pubsub import AsyncPubSub


@pytest.mark.asyncio
class TestAsyncPubSub:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.pubsub = AsyncPubSub()
        yield
        # No teardown needed

    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self):
        received = []

        async def subscriber(msg):
            received.append(msg)

        self.pubsub.subscribe("test", subscriber)
        await self.pubsub.async_publish("test", "hello")
        await asyncio.sleep(0.01)  # allow subscriber to run
        assert received == ["hello"]

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        received1, received2 = [], []

        async def sub1(msg):
            received1.append(msg)

        async def sub2(msg):
            received2.append(msg)

        self.pubsub.subscribe("test", sub1)
        self.pubsub.subscribe("test", sub2)
        await self.pubsub.async_publish("test", "hi")
        await asyncio.sleep(0.01)
        assert received1 == ["hi"]
        assert received2 == ["hi"]

    @pytest.mark.asyncio
    async def test_subscriber_exception(self):
        async def bad_sub(msg):
            raise Exception("fail")

        self.pubsub.subscribe("test", bad_sub)
        # Should not raise
        await self.pubsub.async_publish("test", "test")

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        async def sub(msg):
            pass

        subscriber = self.pubsub.subscribe("test", sub)
        self.pubsub.unsubscribe(subscriber)
        assert subscriber not in self.pubsub.subscribers.get("test", [])
