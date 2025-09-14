# src: tests/integration/client/test_alpaca_portfolio_client.py


from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_portfolio_client import (
    AlpacaPortfolioClient,
)
from algo_royale.models.alpaca_trading.alpaca_portfolio import PortfolioPerformance
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaPortfolioClient(
        logger=MockLoggable(),
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    fake_performance = PortfolioPerformance(
        timestamp=[1, 2, 3],
        equity=[1000.0, 1010.0, 1020.0],
        profit_loss=[0.0, 10.0, 20.0],
        profit_loss_pct=[0.0, 0.01, 0.02],
        base_value=1000.0,
        timeframe="1D",
        base_value_asof=datetime.now(),
    )
    monkeypatch.setattr(
        client, "fetch_portfolio_history", AsyncMock(return_value=fake_performance)
    )
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaPortfolioClientIntegration:
    async def test_fetch_portfolio_history(self, alpaca_client):
        """Test fetching portfolio history data from Alpaca's live endpoint."""

        result = await alpaca_client.fetch_portfolio_history(
            period="1M", timeframe="1D"
        )

        assert result is not None
        assert isinstance(result, PortfolioPerformance)

        expected_attrs = [
            "timestamp",
            "equity",
            "profit_loss",
            "profit_loss_pct",
            "base_value",
            "timeframe",
            "base_value_asof",
        ]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing expected attribute: {attr}"
            assert getattr(result, attr) is not None, f"{attr} is None"
            assert isinstance(getattr(result, attr), list) or isinstance(
                getattr(result, attr), (float, str, datetime)
            ), f"{attr} is not the expected type"
