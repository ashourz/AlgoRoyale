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


class StageDataContainer:
    def __init__(
        self, config, logger_container: LoggerContainer, repo_container: RepoContainer
    ):
        self.config = config
        self.logger_container = logger_container
        self.repo_container = repo_container

        self.data_dir = get_project_root() / self.config.data_dir.root()

        self.stage_data_manager = StageDataManager(
            data_dir=self.data_dir,
            logger=self.logger_container.logger(
                logger_type=LoggerType.STAGE_DATA_MANAGER
            ),
        )

        self.stage_data_preparer = StageDataPreparer(
            stage_data_manager=self.stage_data_manager,
            logger=self.logger_container.logger(
                logger_type=LoggerType.STAGE_DATA_PREPARER
            ),
        )

        self.stage_data_loader = StageDataLoader(
            logger=self.logger_container.logger(
                logger_type=LoggerType.STAGE_DATA_LOADER
            ),
            stage_data_manager=self.stage_data_manager,
            watchlist_repo=self.repo_container.watchlist_repo,
        )

        self.stage_data_writer = StageDataWriter(
            logger=self.logger_container.logger(
                logger_type=LoggerType.STAGE_DATA_WRITER
            ),
            stage_data_manager=self.stage_data_manager,
        )

        self.symbol_strategy_manager = SymbolStrategyManager(
            data_dir=self.data_dir,
            stage_data_manager=self.stage_data_manager,
            symbol_strategy_evaluation_filename=self.config.backtester_signal_filenames.signal_evaluation_json_filename,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SYMBOL_STRATEGY_DATA_MANAGER
            ),
        )

        self.symbol_strategy_data_loader = SymbolStrategyDataLoader(
            stage_data_manager=self.stage_data_manager,
            stage_data_loader=self.stage_data_loader,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SYMBOL_STRATEGY_DATA_LOADER
            ),
        )

        self.symbol_strategy_data_writer = SymbolStrategyDataWriter(
            stage_data_manager=self.stage_data_manager,
            data_writer=self.stage_data_writer,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SYMBOL_STRATEGY_DATA_WRITER
            ),
        )
