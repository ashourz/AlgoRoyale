from algo_royale.application.orders.order_generator import OrderGenerator
from algo_royale.application.signals.signal_generator import SignalGenerator
from algo_royale.logging.loggable import Loggable


class OrderGeneratorService:
    def __init__(
        self,
        signal_generator: SignalGenerator,
        order_generator: OrderGenerator,
        logger: Loggable,
    ):
        self.logger = logger
        self.order_generator = order_generator
