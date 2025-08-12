from algo_royale.application.orders.order_generator import OrderGenerator
from algo_royale.logging.loggable import Loggable
from algo_royale.trader.ledger.ledger import Ledger


class OrderExecution:
    def __init__(
        self,
        order_generator: OrderGenerator,
        ledger: Ledger,
        logger: Loggable,
    ):
        """
        Initialize the OrderExecution with an order generator and a logger.

        :param order_generator: An instance of OrderGenerator to generate symbol order payloads.
        :param logger: Loggable instance for logging messages and errors.
        """
        self.order_generator = order_generator
        self.ledger = ledger
        self.logger = logger
