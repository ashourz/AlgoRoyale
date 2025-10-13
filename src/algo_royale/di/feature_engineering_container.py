from functools import partial

from algo_royale.backtester.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)
from algo_royale.backtester.feature_engineering.backtest_feature_engineer import (
    BacktestFeatureEngineer,
)
from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer
from algo_royale.backtester.feature_engineering.feature_engineering import (
    feature_engineering,
)
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType


class FeatureEngineeringContainer:
    def __init__(self, config, logger_container: LoggerContainer):
        self.config = config
        self.logger_container = logger_container

    @property
    def feature_engineering_func(self):
        return partial(feature_engineering)

    @property
    def backtest_feature_engineer(self) -> BacktestFeatureEngineer:
        return BacktestFeatureEngineer(
            feature_engineering_func=self.feature_engineering_func,
            logger=self.logger_container.logger(
                logger_type=LoggerType.BACKTEST_FEATURE_ENGINEERING
            ),
            max_lookback=FeatureEngineeringColumns.get_max_lookback_from_columns(),
        )

    @property
    def feature_engineer(self) -> FeatureEngineer:
        return FeatureEngineer(
            logger=self.logger_container.logger(logger_type=LoggerType.FEATURE_ENGINEER)
        )
