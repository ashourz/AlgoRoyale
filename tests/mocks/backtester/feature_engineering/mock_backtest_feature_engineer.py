from algo_royale.backtester.feature_engineering.backtest_feature_engineer import (
    BacktestFeatureEngineer,
)


class MockBacktestFeatureEngineer(BacktestFeatureEngineer):
    def __init__(self):
        self.should_raise = False
        self.should_return_none = False
        self.return_value = {"mock": True}

    def set_raise(self, value: bool):
        self.should_raise = value

    def set_return_none(self, value: bool):
        self.should_return_none = value

    def set_return_value(self, value):
        self.return_value = value

    def engineer_features(self, *args, **kwargs):
        if self.should_raise:
            raise RuntimeError("Mocked exception in engineer_features")
        if self.should_return_none:
            return None
        return self.return_value
