import pytest

from tests.mocks.services.mock_ledger_service import MockLedgerService


@pytest.fixture
def ledger_service():
    service = MockLedgerService()
    yield service


@pytest.mark.asyncio
class TestLedgerService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, ledger_service: MockLedgerService):
        print("Setup")
        ledger_service.reset()
        yield
        print("Teardown")
        ledger_service.reset()

    async def test_get_current_positions_normal(
        self, ledger_service: MockLedgerService
    ):
        positions = ledger_service.get_current_position(symbol="AAPL")
        assert positions == 1
