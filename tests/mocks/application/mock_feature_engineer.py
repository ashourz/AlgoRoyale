from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer
from tests.mocks.mock_loggable import MockLoggable


class MockFeatureEngineer(FeatureEngineer):
    def __init__(self):
        super().__init__(logger=MockLoggable())
