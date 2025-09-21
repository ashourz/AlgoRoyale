from dependency_injector import containers, providers

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
from algo_royale.utils.path_utils import get_project_root


class ApplicationContainer(containers.DynamicContainer):
    def __init__(self, environment=ApplicationEnv):
        super().__init__()
        self.environment = providers.Object(environment)
        self.config = providers.Configuration()
        self.secrets = providers.Configuration()

        self.logger_container = providers.Container(
            LoggerContainer,
            environment=self.environment,
        )

        self.repo_container = providers.Container(
            RepoContainer,
            config=self.config,
            secrets=self.secrets,
            logger_container=self.logger_container,
        )

        self.adapter_container = providers.Container(
            AdapterContainer,
            config=self.config,
            secrets=self.secrets,
            logger_container=self.logger_container,
        )

        self.clock_service = providers.Singleton(
            ClockService,
            clock_adapter=self.adapter_container.clock_adapter,
            logger=providers.Factory(
                self.logger_container.logger,
                logger_type=LoggerType.CLOCK_SERVICE,
            ),
        )

        self.stage_data_container = providers.Container(
            StageDataContainer,
            config=self.config,
            logger_container=self.logger_container,
            repo_container=self.repo_container,
        )

        self.factory_container = providers.Container(
            FactoryContainer,
            config=self.config,
            logger_container=self.logger_container,
        )

        self.feature_engineering_container = providers.Container(
            FeatureEngineeringContainer,
            config=self.config,
            logger_container=self.logger_container,
        )

        self.backtest_pipeline_container = providers.Container(
            BacktestPipelineContainer,
            config=self.config,
            stage_data_container=self.stage_data_container,
            feature_engineering_container=self.feature_engineering_container,
            factory_container=self.factory_container,
            adapter_container=self.adapter_container,
            repo_container=self.repo_container,
            logger_container=self.logger_container,
        )

        self.ledger_service_container = providers.Container(
            LedgerServiceContainer,
            config=self.config,
            adapter_container=self.adapter_container,
            repo_container=self.repo_container,
            logger_container=self.logger_container,
            clock_service=self.clock_service,
        )

        self.trading_container = providers.Container(
            TradingContainer,
            config=self.config,
            adapter_container=self.adapter_container,
            repo_container=self.repo_container,
            feature_engineering_container=self.feature_engineering_container,
            stage_data_container=self.stage_data_container,
            factory_container=self.factory_container,
            ledger_service_container=self.ledger_service_container,
            logger_container=self.logger_container,
            clock_service=self.clock_service,
        )

    def _get_ini_files(self, environment):
        env = environment.value.lower()
        if env == ApplicationEnv.PROD_LIVE.value.lower():
            return "env_config_prod_live.ini", "env_secrets_prod_live.ini"
        elif env == ApplicationEnv.PROD_PAPER.value.lower():
            return "env_config_prod_paper.ini", "env_secrets_prod_paper.ini"
        elif env == ApplicationEnv.DEV_INTEGRATION.value.lower():
            return "env_config_dev_integration.ini", "env_secrets_dev_integration.ini"
        else:
            raise ValueError(f"Unsupported environment: {environment}")

    def setup_configs(self):
        ini_file, secret_file = self._get_ini_files(self.environment())
        config_dir = get_project_root() / "src/algo_royale/config"
        ini_file = config_dir / ini_file
        secret_file = config_dir / secret_file
        self.config.from_ini(ini_file)
        self.secrets.from_ini(secret_file)
