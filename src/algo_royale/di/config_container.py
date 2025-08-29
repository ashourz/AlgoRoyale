from dependency_injector import containers, providers

from algo_royale.clients.alpaca.alpaca_client_config import TradingConfig
from algo_royale.config.config import Config


class ConfigContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Config, config_file="config.ini")
    secrets = providers.Singleton(Config, config_file="secrets.ini")
    trading_config = providers.Singleton(
        TradingConfig,
        config=config,
        secrets=secrets,
    )
