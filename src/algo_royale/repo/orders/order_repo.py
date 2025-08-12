from logging import Logger


class OrderRepo:
    def __init__(self, orders_service logger: Logger):
        self.account_service = account_service
        self.logger = logger

    async def buying_power(self) -> Decimal:
        """Get the current buying power of the account."""
        return self.buying_power
