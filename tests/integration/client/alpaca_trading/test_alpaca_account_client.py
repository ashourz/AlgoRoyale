# src: tests/integration/client/test_alpaca_account_client.py

import logging
import pytest
from algo_royale.client.alapaca_trading.alpaca_accounts_client import AlpacaAccountClient
from models.alpaca_trading.alpaca_account import Account

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaAccountClient()

@pytest.mark.asyncio
class TestAlpacaAccountClientIntegration:

    def test_fetch_account(self, alpaca_client):
        """Test fetching account data from Alpaca's live endpoint."""

        result = alpaca_client.fetch_account()

        assert result is not None
        assert isinstance(result, Account)

        expected_attrs = [
            "id", "account_number", "status", "crypto_status", "currency",
            "cash", "portfolio_value", "non_marginable_buying_power", "accrued_fees",
            "pending_transfer_in", "pending_transfer_out", "pattern_day_trader",
            "trade_suspended_by_user", "trading_blocked", "transfers_blocked",
            "account_blocked", "created_at", "shorting_enabled", "long_market_value",
            "short_market_value", "equity", "last_equity", "multiplier",
            "buying_power", "initial_margin", "maintenance_margin", "sma",
            "daytrade_count", "last_maintenance_margin", "daytrading_buying_power",
            "regt_buying_power"
        ]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing expected attribute: {attr}"
            assert getattr(result, attr) is not None, f"{attr} is None"    