from dependency_injector import containers, providers

from algo_royale.backtester.data_preparer.stage_data_preparer import StageDataPreparer
from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.writer.stage_data_writer import StageDataWriter
from algo_royale.backtester.stage_data.writer.symbol_strategy_data_writer import (
    SymbolStrategyDataWriter,
)
from algo_royale.backtester.strategy.signal.manager.symbol_strategy_manager import (
    SymbolStrategyManager,
)
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.repo_container import RepoContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.utils.path_utils import get_project_root


class StageDataContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger_container: LoggerContainer = providers.DependenciesContainer()
    repo_container: RepoContainer = providers.DependenciesContainer()

    def get_data_dir(config) -> str:
        return get_project_root() / config.data_dir.root()

    data_dir = providers.Callable(get_data_dir, config=config)

    stage_data_manager = providers.Singleton(
        StageDataManager,
        data_dir=data_dir,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.STAGE_DATA_MANAGER
        ),
    )

    stage_data_preparer = (
        providers.Singleton(
            StageDataPreparer,
            stage_data_manager=stage_data_manager,
            logger=providers.Factory(
                logger_container.logger, logger_type=LoggerType.STAGE_DATA_PREPARER
            ),
        ),
    )

    stage_data_loader = providers.Singleton(
        StageDataLoader,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.STAGE_DATA_LOADER
        ),
        stage_data_manager=stage_data_manager,
        watchlist_repo=repo_container.watchlist_repo,
    )

    stage_data_writer = providers.Singleton(
        StageDataWriter,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.STAGE_DATA_WRITER
        ),
        stage_data_manager=stage_data_manager,
    )

    symbol_strategy_manager = providers.Singleton(
        SymbolStrategyManager,
        data_dir=data_dir,
        stage_data_manager=stage_data_manager,
        symbol_strategy_evaluation_filename=config.backtester_signal_filenames.signal_evaluation_json_filename,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.SYMBOL_STRATEGY_DATA_MANAGER
        ),
    )

    symbol_strategy_data_loader = providers.Singleton(
        SymbolStrategyDataLoader,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.SYMBOL_STRATEGY_DATA_LOADER
        ),
    )

    symbol_strategy_data_writer = providers.Singleton(
        SymbolStrategyDataWriter,
        stage_data_manager=stage_data_manager,
        data_writer=stage_data_writer,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.SYMBOL_STRATEGY_DATA_WRITER
        ),
    )
