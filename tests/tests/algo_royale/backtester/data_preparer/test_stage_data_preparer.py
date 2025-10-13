from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.data_preparer.stage_data_preparer import StageDataPreparer
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def stage_data_preparer():
    preparer = StageDataPreparer(
        stage_data_manager=MockStageDataManager(),
        logger=MockLoggable(),
    )
    yield preparer


def set_stage_data_manager_return_false(preparer: StageDataPreparer, value: bool):
    preparer.stage_data_manager.set_return_false(value)


def reset_stage_data_manager_return_false(preparer: StageDataPreparer):
    preparer.stage_data_manager.reset_return_false()


def set_stage_data_manager_return_none(preparer: StageDataPreparer, value: bool):
    preparer.stage_data_manager.set_return_none(value)


def reset_stage_data_manager_return_none(preparer: StageDataPreparer):
    preparer.stage_data_manager.reset_return_none()


def reset_stage_data_preparer(preparer: StageDataPreparer):
    preparer.stage_data_manager.reset()


@pytest.mark.asyncio
class TestStageDataPreparer:
    @pytest.mark.asyncio
    async def test_normalize_stream_valid(self, stage_data_preparer):
        # Mock BacktestStage with required input_columns
        class DummyStage:
            input_columns = ["col1", "col2"]

        # Async iterator yielding valid DataFrame
        async def async_iter():
            yield pd.DataFrame({"col1": [1], "col2": [2]})

        result = []
        async for df in stage_data_preparer.normalize_stream(
            DummyStage, lambda: async_iter()
        ):
            result.append(df)
        assert len(result) == 1
        assert list(result[0].columns) == ["col1", "col2"]

    @pytest.mark.asyncio
    async def test_normalize_stream_missing_columns(self, stage_data_preparer):
        class DummyStage:
            input_columns = ["col1", "col2"]

        # Async iterator yielding DataFrame missing a column
        async def async_iter():
            yield pd.DataFrame({"col1": [1]})

        # Should skip invalid DataFrame, so result is empty
        result = []
        async for df in stage_data_preparer.normalize_stream(
            DummyStage, lambda: async_iter()
        ):
            result.append(df)
        assert result == []

    @pytest.mark.asyncio
    async def test_normalize_stream_type_error(self, stage_data_preparer):
        class DummyStage:
            input_columns = ["col1"]

        # Not an async iterator
        def not_async_iter():
            return iter([pd.DataFrame({"col1": [1]})])

        with pytest.raises(TypeError):
            async for _ in stage_data_preparer.normalize_stream(
                DummyStage, not_async_iter
            ):
                pass

    def test_normalize_stage_data_success(self, stage_data_preparer):
        # Prepare dummy async iterator factory
        class DummyStage:
            input_columns = ["col1"]

        async def async_iter():
            yield pd.DataFrame({"col1": [1]})

        data = {"AAPL": lambda: async_iter()}
        result = stage_data_preparer.normalize_stage_data(
            DummyStage, data, strategy_name="strat1"
        )
        assert "AAPL" in result
        # The factory should return an async generator
        gen = result["AAPL"]()
        assert hasattr(gen, "__aiter__")

    @pytest.mark.asyncio
    async def test_normalize_stage_data_error_factory_raises(self, stage_data_preparer):
        # Factory that raises immediately
        class DummyStage:
            input_columns = ["col1"]

        def bad_factory():
            raise ValueError("fail!")

        data = {"AAPL": bad_factory}
        stage_data_preparer.stage_data_manager.write_error_file = MagicMock()
        result = stage_data_preparer.normalize_stage_data(
            DummyStage, data, strategy_name="strat1"
        )
        with pytest.raises(ValueError):
            async for _ in result["AAPL"]():
                pass
        assert stage_data_preparer.stage_data_manager.write_error_file.called

    @pytest.mark.asyncio
    async def test_normalize_stage_data_error_async_iter_raises(
        self, stage_data_preparer
    ):
        # Factory returns async generator that raises during iteration
        class DummyStage:
            input_columns = ["col1"]

        async def async_iter():
            raise ValueError("fail in async iter!")
            yield  # unreachable

        data = {"AAPL": lambda: async_iter()}
        stage_data_preparer.stage_data_manager.write_error_file = MagicMock()
        result = stage_data_preparer.normalize_stage_data(
            DummyStage, data, strategy_name="strat1"
        )
        with pytest.raises(ValueError):
            async for _ in result["AAPL"]():
                pass
        # In this case, write_error_file is NOT called, because the error is in the async generator, not the factory

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, stage_data_preparer: StageDataPreparer):
        print("Setup: Resetting StageDataPreparer")
        stage_data_preparer.stage_data_manager.reset()
        yield
        print("Teardown: Resetting StageDataPreparer")
        stage_data_preparer.stage_data_manager.reset()

    @pytest.mark.asyncio
    async def test_normalize_stream_data_normal(
        self, stage_data_preparer: StageDataPreparer
    ):
        class DummyStage:
            input_columns = ["col1", "col2"]

        async def async_iter():
            yield pd.DataFrame({"col1": [1], "col2": [2]})

        result = []
        async for df in stage_data_preparer.normalize_stream(
            DummyStage, lambda: async_iter()
        ):
            result.append(df)
        assert len(result) == 1
        assert list(result[0].columns) == ["col1", "col2"]
