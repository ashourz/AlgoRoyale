import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.data_staging.feature_engineering_stage_coordinator import (
    FeatureEngineeringStageCoordinator,
)
from tests.mocks.backtester.feature_engineering.mock_backtest_feature_engineer import (
    MockBacktestFeatureEngineer,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.stage_data.loader.mock_symbol_strategy_data_loader import (
    MockSymbolStrategyDataLoader,
)
from tests.mocks.backtester.stage_data.writer.mock_symbol_strategy_data_writer import (
    MockSymbolStrategyDataWriter,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def mock_logger():
    return MockLoggable()


@pytest.fixture
def mock_data_loader():
    return MockSymbolStrategyDataLoader()


@pytest.fixture
def mock_data_writer():
    return MockSymbolStrategyDataWriter()


@pytest.fixture
def mock_stage_data_manager():
    return MockStageDataManager()


@pytest.fixture
def mock_feature_engineer():
    return MockBacktestFeatureEngineer()


@pytest.fixture
def coordinator(
    mock_logger,
    mock_data_loader,
    mock_data_writer,
    mock_stage_data_manager,
    mock_feature_engineer,
):
    return FeatureEngineeringStageCoordinator(
        data_loader=mock_data_loader,
        data_writer=mock_data_writer,
        data_manager=mock_stage_data_manager,
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
    # prepared_data: symbol -> factory returning async generator
    async def async_gen():
        yield pd.DataFrame({"a": [1]})

    def factory():
        return async_gen()

    prepared_data = {"AAPL": factory}

    # Patch engineer_features to yield the same as async_gen
    def patched_engineer_features(df_iter, symbol):
        return async_gen()

    mock_feature_engineer.engineer_features = patched_engineer_features
    result = await coordinator._process(prepared_data)
    out = []
    async for df in result["AAPL"][None]():
        out.append(df)
    assert isinstance(out[0], pd.DataFrame)


@pytest.mark.asyncio
async def test_process_engineer_returns_empty(coordinator, mock_feature_engineer):
    # Patch _engineer to return empty dict
    async def empty_engineer(*args, **kwargs):
        return {}

    coordinator._engineer = empty_engineer
    result = await coordinator._process({"AAPL": lambda: None})
    assert result == {}
    assert any("Feature engineering failed" in m for m in coordinator.logger.messages)


@pytest.mark.asyncio
async def test_engineer_returns_factories(
    coordinator, mock_feature_engineer, async_gen_factory
):
    async def async_gen():
        yield pd.DataFrame({"a": [1]})

    def factory():
        return async_gen()

    ingest_data = {"AAPL": factory}

    def patched_engineer_features(df_iter, symbol):
        return async_gen()

    mock_feature_engineer.engineer_features = patched_engineer_features
    engineered = await coordinator._engineer(ingest_data)
    assert "AAPL" in engineered
    out = []
    async for df in engineered["AAPL"]():
        out.append(df)
    assert isinstance(out[0], pd.DataFrame)


# Error/exception handling tests
@pytest.mark.asyncio
async def test_engineer_features_raises_exception(coordinator, mock_feature_engineer):
    mock_feature_engineer.set_raise(True)

    async def async_gen():
        yield pd.DataFrame({"a": [1]})

    def factory():
        return async_gen()

    ingest_data = {"AAPL": factory}
    result = await coordinator._engineer(ingest_data)
    assert "AAPL" in result
    with pytest.raises(RuntimeError, match="Mocked exception in engineer_features"):
        async for _ in result["AAPL"]():
            pass
