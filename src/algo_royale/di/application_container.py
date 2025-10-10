import configparser

from algo_royale.di.adapter.adapter_container import AdapterContainer
from algo_royale.di.backtest.backtest_pipeline_container import (
    BacktestPipelineContainer,
)
from algo_royale.di.factory_container import FactoryContainer
from algo_royale.di.feature_engineering_container import FeatureEngineeringContainer
from algo_royale.di.ledger_service_container import LedgerServiceContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.repo_container import RepoContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.di.trading.trading_container import TradingContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.clock_service import ClockService
from algo_royale.utils.clock_provider import ClockProvider


class ApplicationContainer:
    def __init__(self, environment: ApplicationEnv):
        self.environment = environment

        # Load config and secrets as dicts
        config_parser = configparser.ConfigParser()
        config_parser.read(self.environment.config_ini_path)
        self.config = self._to_dict(config_parser)
        if self.config == {}:
            raise ValueError(
                f"Config file at {self.environment.config_ini_path} is empty or invalid."
            )
        secrets_parser = configparser.ConfigParser()
        secrets_parser.read(self.environment.secrets_ini_path)
        self.secrets = self._to_dict(secrets_parser)
        if self.secrets == {}:
            raise ValueError(
                f"Secrets file at {self.environment.secrets_ini_path} is empty or invalid."
            )

    @property
    def clock_provider(self) -> ClockProvider:
        return ClockProvider()

    @property
    def logger_container(self) -> LoggerContainer:
        return LoggerContainer(environment=self.environment)

    @property
    def repo_container(self) -> RepoContainer:
        return RepoContainer(
            config=self.config,
            secrets=self.secrets,
            logger_container=self.logger_container,
        )

    @property
    def adapter_container(self) -> AdapterContainer:
        return AdapterContainer(
            config=self.config,
            secrets=self.secrets,
            clock_provider=self.clock_provider,
            logger_container=self.logger_container,
        )

    @property
    def clock_service(self) -> ClockService:
        return ClockService(
            clock_adapter=self.adapter_container.clock_adapter,
            clock_provider=self.clock_provider,
            logger=self.logger_container.logger(logger_type=LoggerType.CLOCK_SERVICE),
        )

    @property
    def stage_data_container(self) -> StageDataContainer:
        return StageDataContainer(
            config=self.config,
            logger_container=self.logger_container,
            repo_container=self.repo_container,
        )

    @property
    def factory_container(self) -> FactoryContainer:
        return FactoryContainer(
            config=self.config,
            logger_container=self.logger_container,
        )

    @property
    def feature_engineering_container(self) -> FeatureEngineeringContainer:
        return FeatureEngineeringContainer(
            config=self.config,
            logger_container=self.logger_container,
        )

    @property
    def backtest_pipeline_container(self) -> BacktestPipelineContainer:
        return BacktestPipelineContainer(
            config=self.config,
            stage_data_container=self.stage_data_container,
            feature_engineering_container=self.feature_engineering_container,
            factory_container=self.factory_container,
            adapter_container=self.adapter_container,
            repo_container=self.repo_container,
            clock_service=self.clock_service,
            logger_container=self.logger_container,
        )

    @property
    def ledger_service_container(self) -> LedgerServiceContainer:
        return LedgerServiceContainer(
            config=self.config,
            adapter_container=self.adapter_container,
            repo_container=self.repo_container,
            logger_container=self.logger_container,
            clock_service=self.clock_service,
        )

    @property
    def trading_container(self) -> TradingContainer:
        return TradingContainer(
            config=self.config,
            adapter_container=self.adapter_container,
            repo_container=self.repo_container,
            feature_engineering_container=self.feature_engineering_container,
            stage_data_container=self.stage_data_container,
            factory_container=self.factory_container,
            ledger_service_container=self.ledger_service_container,
            logger_container=self.logger_container,
            clock_service=self.clock_service,
            clock_provider=self.clock_provider,
        )

    async def async_close(self):
        """Close resources like database connections."""
        self.repo_container.close()
        await self.adapter_container.async_close()

    def _to_dict(self, config_parser):
        # Convert ConfigParser to a nested dict for compatibility
        result = {}
        for section in config_parser.sections():
            result[section] = dict(config_parser.items(section))
        return result
