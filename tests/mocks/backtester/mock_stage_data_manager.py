from pathlib import Path

from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from tests.mocks.mock_loggable import MockLoggable


class MockStageDataManager(StageDataManager):
    def __init__(self, data_dir: Path):
        super().__init__(data_dir=data_dir, logger=MockLoggable())
        self._mock_files = {}
        self._mock_deleted = set()

    def reset(self):
        self._mock_files.clear()
        self._mock_deleted.clear()

    # Optionally override methods for more controlled test behavior
    def write_file(self, *args, **kwargs):
        # Assume the last positional argument is the content
        *key, content = args
        self._mock_files[tuple(key)] = content
        return True

    def read_file(self, *args, **kwargs):
        return self._mock_files.get(tuple(args), None)

    def delete_file(self, *args, **kwargs):
        key = tuple(args)
        self._mock_deleted.add(key)
        if key in self._mock_files:
            del self._mock_files[key]
        return True

    def file_exists(self, *args, **kwargs):
        key = tuple(args)
        return key in self._mock_files
