import pandas as pd

from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from tests.mocks.mock_loggable import MockLoggable


class MockAssetMatrixPreparer(AssetMatrixPreparer):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(logger=self.logger)
        self.raise_exception = False
        self.return_none = False
        self.default_df = pd.DataFrame({"mock": [1, 2, 3]})
        self.df = self.default_df

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def set_return_none(self, value: bool):
        self.return_none = value

    def set_dataframe(self, df: pd.DataFrame):
        self.df = df

    def reset(self):
        self.raise_exception = False
        self.return_none = False
        self.df = self.default_df

    def prepare(self, data):
        if self.raise_exception:
            raise ValueError("Mocked exception")
        if self.return_none:
            return None
        return self.df
