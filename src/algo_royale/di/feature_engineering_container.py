from functools import partial

from dependency_injector import containers, providers

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


class FeatureEngineeringContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger_container: LoggerContainer = providers.DependenciesContainer()

    feature_engineering_func = providers.Object(partial(feature_engineering))

    backtest_feature_engineer = providers.Singleton(
        BacktestFeatureEngineer,
        feature_engineering_func=feature_engineering_func,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.BACKTEST_FEATURE_ENGINEERING
        ),
        max_lookback=FeatureEngineeringColumns.get_max_lookback_from_columns(),
    )

    feature_engineer = providers.Singleton(
        FeatureEngineer,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.FEATURE_ENGINEER
        ),
    )
