
from dependency_injector.wiring import inject, Provide
from algo_royale.di.container import DIContainer
from algo_royale.services.trading.alpaca_orders_service import AlpacaOrdersService

# @inject
# def place_order(
#     symbol: str,
#     qty: int,
#     side: str,
#     type: str,
#     time_in_force: str,
#     orders_service: AlpacaOrdersService = Provide[DIContainer.alpaca_orders_service],
# ):
#     """Place an order using AlpacaOrdersService."""
#     orders_service.place_order(symbol, qty, side, type, time_in_force) 