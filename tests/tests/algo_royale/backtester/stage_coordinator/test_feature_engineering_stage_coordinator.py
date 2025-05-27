from unittest.mock import ANY, AsyncMock, MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.feature_engineering_stage_coordinator import (
    FeatureEngineeringStageCoordinator,
)


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_data_loader():
    return MagicMock()


@pytest.fixture
def mock_data_preparer():
    return MagicMock()


@pytest.fixture
def mock_data_writer():
    return MagicMock()


@pytest.fixture
def mock_stage_data_manager():
    return MagicMock()


@pytest.fixture
def mock_feature_engineer():
    engineer = MagicMock()

    # Use a real async generator function for engineer_features
    async def engineer_features(df_iter, symbol):
        async for df in df_iter:
            yield df

    engineer.engineer_features = MagicMock(side_effect=engineer_features)
    return engineer


@pytest.fixture
def coordinator(
    mock_logger,
    mock_data_loader,
    mock_data_preparer,
    mock_data_writer,
    mock_stage_data_manager,
    mock_feature_engineer,
):
    return FeatureEngineeringStageCoordinator(
        config={},
        data_loader=mock_data_loader,
        data_preparer=mock_data_preparer,
        data_writer=mock_data_writer,
        stage_data_manager=mock_stage_data_manager,
        logger=mock_logger,
        feature_engineer=mock_feature_engineer,
    )


@pytest.fixture
def async_gen_factory():
    async def async_gen():
        yield pd.DataFrame({"a": [1]})

    return async_gen


@pytest.mark.asyncio
async def test_process_success(coordinator, mock_feature_engineer, async_gen_factory):
    mock_feature_engineer.engineer_features.side_effect = (
        lambda df_iter, symbol: async_gen_factory()
    )

    # prepared_data: symbol -> factory returning async generator
    prepared_data = {"AAPL": async_gen_factory}
    result = await coordinator.process(prepared_data)
    out = []
    async for df in result["AAPL"]():
        out.append(df)
    assert isinstance(out[0], pd.DataFrame)


@pytest.mark.asyncio
async def test_process_engineer_returns_empty(coordinator, mock_feature_engineer):
    # Patch _engineer to return empty dict
    coordinator._engineer = AsyncMock(return_value={})
    result = await coordinator.process({"AAPL": lambda: None})
    assert result == {}
    coordinator.logger.error.assert_called_with("Feature engineering failed")


@pytest.mark.asyncio
async def test_engineer_returns_factories(
    coordinator, mock_feature_engineer, async_gen_factory
):
    mock_feature_engineer.engineer_features.side_effect = (
        lambda df_iter, symbol: async_gen_factory()
    )

    ingest_data = {"AAPL": lambda: async_gen_factory()}

    engineered = await coordinator._engineer(ingest_data)
    assert "AAPL" in engineered
    out = []
    async for df in engineered["AAPL"]():
        out.append(df)
    assert isinstance(out[0], pd.DataFrame)
    # This will now work:
    mock_feature_engineer.engineer_features.assert_called_with(ANY, "AAPL")
