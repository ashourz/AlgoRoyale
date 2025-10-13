from typing import Callable, Dict, List

from algo_royale.application.utils.async_pubsub import AsyncSubscriber


class SymbolSubscriberManager:
    def __init__(self):
        self.upstream_subscriber_map: Dict[str, list[AsyncSubscriber]] = {}
        self.downstream_subscriber_map: Dict[str, list[AsyncSubscriber]] = {}

    async def subscribe(
        self, symbols: List[str], callback: Callable
    ) -> Dict[str, AsyncSubscriber]:
        result = {}
        for symbol in symbols:
            if not self._can_subscribe(symbol):
                continue
            if symbol in self.upstream_subscriber_map:
                result[symbol] = self.upstream_subscriber_map[symbol]
            else:
                subscriber = await self._create_subscriber(symbol, callback)
                if subscriber:
                    self.subscriber_map[symbol] = subscriber
                    result[symbol] = subscriber
        return result

    def _can_subscribe(self, symbol: str) -> bool:
        # Override: check for valid strategy, etc.
        return True

    async def _create_subscriber(
        self, symbol: str, callback: Callable
    ) -> AsyncSubscriber | None:
        # Override: actual subscription logic
        pass

    async def unsubscribe(self, symbol_subscribers: Dict[str, AsyncSubscriber]):
        for symbol, subscriber in symbol_subscribers.items():
            await self._remove_subscriber(symbol, subscriber)
            self.subscriber_map.pop(symbol, None)

    def _can_unsubscribe(self, symbol: str) -> bool:
        # Override: check for valid strategy, etc.
        return True

    async def _remove_subscriber(self, symbol: str, subscriber: AsyncSubscriber):
        # Override: actual unsubscription logic
        pass
