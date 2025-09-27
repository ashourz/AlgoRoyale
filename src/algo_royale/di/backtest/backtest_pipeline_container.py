from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from algo_royale.di.backtest.data_prep_coordinator_container import (
    DataPrepCoordinatorContainer,
)
from algo_royale.di.backtest.portfolio_backtest_container import (
    PortfolioBacktestContainer,
)
from algo_royale.di.backtest.signal_backtest_container import SignalBacktestContainer
from algo_royale.logging.logger_type import LoggerType


# Refactored to a regular class
class BacktestPipelineContainer:
    def __init__(
        self,
        config,
        stage_data_container,
        feature_engineering_container,
        factory_container,
        adapter_container,
        repo_container,
        logger_container,
    ):
        self.config = config
        self.stage_data_container = stage_data_container
        self.feature_engineering_container = feature_engineering_container
        self.factory_container = factory_container
        self.adapter_container = adapter_container
        self.repo_container = repo_container
        self.logger_container = logger_container

    @property
    def data_prep_coordinator_container(self) -> DataPrepCoordinatorContainer:
        return DataPrepCoordinatorContainer(
            config=self.config,
            logger_container=self.logger_container,
            stage_data_container=self.stage_data_container,
            feature_engineering_container=self.feature_engineering_container,
            adapter_container=self.adapter_container,
            repo_container=self.repo_container,
        )

    @property
    def signal_backtest_container(self) -> SignalBacktestContainer:
        return SignalBacktestContainer(
            config=self.config,
            data_prep_coordinator_container=self.data_prep_coordinator_container,
            stage_data_container=self.stage_data_container,
            factory_container=self.factory_container,
            logger_container=self.logger_container,
        )

    @property
    def portfolio_backtest_container(self) -> PortfolioBacktestContainer:
        return PortfolioBacktestContainer(
            config=self.config,
            data_prep_coordinator_container=self.data_prep_coordinator_container,
            stage_data_container=self.stage_data_container,
            signal_backtest_container=self.signal_backtest_container,
            factory_container=self.factory_container,
            logger_container=self.logger_container,
        )

    @property
    def pipeline_coordinator(self) -> PipelineCoordinator:
        return PipelineCoordinator(
            signal_strategy_walk_forward_coordinator=self.signal_backtest_container.signal_strategy_walk_forward_coordinator,
            portfolio_walk_forward_coordinator=self.portfolio_backtest_container.portfolio_walk_forward_coordinator,
            signal_strategy_evaluation_coordinator=self.signal_backtest_container.strategy_evaluation_coordinator,
            symbol_evaluation_coordinator=self.signal_backtest_container.symbol_evaluation_coordinator,
            portfolio_evaluation_coordinator=self.portfolio_backtest_container.portfolio_evaluation_coordinator,
            logger=self.logger_container.logger(
                logger_type=LoggerType.PIPELINE_COORDINATOR
            ),
        )
