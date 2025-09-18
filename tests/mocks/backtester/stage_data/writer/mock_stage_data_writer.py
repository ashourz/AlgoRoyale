from unittest.mock import MagicMock

from algo_royale.backtester.stage_data.writer.stage_data_writer import StageDataWriter
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.mock_loggable import MockLoggable


class MockStageDataWriter(StageDataWriter):
    def __init__(self):
        super().__init__(
            logger=MockLoggable(),
            stage_data_manager=MockStageDataManager(data_dir=MagicMock()),
            max_rows_per_file=1000,  # Default value for testing
        )
        self.raise_exception = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def reset(self):
        self.raise_exception = False

    async def async_write_data_batches(
        self, stage, strategy_name, symbol, gen, start_date=None, end_date=None
    ) -> None:
        if self.raise_exception:
            raise Exception("Mocked exception")
        return

    def save_stage_data(
        self,
        stage,
        strategy_name,
        symbol,
        results_df,
        page_idx,
        start_date=None,
        end_date=None,
    ):
        if self.raise_exception:
            raise Exception("Mocked exception")
        return
