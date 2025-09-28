import pytest

from algo_royale.services.order_generator_service import OrderGeneratorService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_symbol_hold_service import MockSymbolHoldService


@pytest.fixture
def market_session_service():
    service = OrderGeneratorService(
        order_generator=MockOrderGenerator(),
        symbol_hold_service=MockSymbolHoldService(),
        logger=MockLoggable(),
    )
    yield service
