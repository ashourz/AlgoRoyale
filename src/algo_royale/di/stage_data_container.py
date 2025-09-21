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
from algo_royale.logging.logger_type import LoggerType
from algo_royale.utils.path_utils import get_project_root


class StageDataContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger_container = providers.DependenciesContainer()
    watchlist_repo = providers.Singleton()

    def get_data_dir(config) -> str:
        return get_project_root() / config.data.dir.root()

    data_dir = providers.Callable(get_data_dir, config=config)

    stage_data_manager = providers.Singleton(
        StageDataManager,
        data_dir=data_dir,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.STAGE_DATA_MANAGER
        ),
    )

    stage_data_preparer = (
        providers.Singleton(
            StageDataPreparer,
            stage_data_manager=stage_data_manager,
            logger=logger_container.logger.provider(
                logger_type=LoggerType.STAGE_DATA_PREPARER
            ),
        ),
    )

    stage_data_loader = providers.Singleton(
        StageDataLoader,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.STAGE_DATA_LOADER
        ),
        stage_data_manager=stage_data_manager,
        watchlist_repo=watchlist_repo,
    )

    stage_data_writer = providers.Singleton(
        StageDataWriter,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.STAGE_DATA_WRITER
        ),
        stage_data_manager=stage_data_manager,
    )

    symbol_strategy_manager = providers.Singleton(
        SymbolStrategyManager,
        data_dir=data_dir,
        stage_data_manager=stage_data_manager,
        symbol_strategy_evaluation_filename=config.backtester.signal.filenames.signal_evaluation_json_filename,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.SYMBOL_STRATEGY_DATA_MANAGER
        ),
    )

    symbol_strategy_data_loader = providers.Singleton(
        SymbolStrategyDataLoader,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.SYMBOL_STRATEGY_DATA_LOADER
        ),
    )

    symbol_strategy_data_writer = providers.Singleton(
        SymbolStrategyDataWriter,
        stage_data_manager=stage_data_manager,
        data_writer=stage_data_writer,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.SYMBOL_STRATEGY_DATA_WRITER
        ),
    )
