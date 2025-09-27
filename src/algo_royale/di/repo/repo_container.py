from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.dao_container import DAOContainer
from algo_royale.di.repo.db_container import DBContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.repo.data_stream_session_repo import DataStreamSessionRepo
from algo_royale.repo.enriched_data_repo import EnrichedDataRepo
from algo_royale.repo.order_repo import OrderRepo
from algo_royale.repo.trade_repo import TradeRepo
from algo_royale.repo.watchlist_repo import WatchlistRepo


class RepoContainer:
    """Repository Container"""

    def __init__(self, config, secrets, logger_container: LoggerContainer):
        self.config = config
        self.secrets = secrets
        self.logger_container = logger_container

    # Instantiate DBContainer and DAOContainer as regular classes (anticipating their refactor)
    @property
    def db_container(self) -> DBContainer:
        return DBContainer(
            config=self.config,
            secrets=self.secrets,
            logger_container=self.logger_container,
        )

    @property
    def dao_container(self) -> DAOContainer:
        return DAOContainer(
            config=self.config,
            db_container=self.db_container,
            logger_container=self.logger_container,
        )

    @property
    def data_stream_session_repo(self) -> DataStreamSessionRepo:
        return DataStreamSessionRepo(
            dao=self.dao_container.data_stream_session_dao,
            logger=self.logger_container.logger(
                logger_type=LoggerType.DATA_STREAM_SESSION_REPO
            ),
        )

    @property
    def enriched_data_repo(self) -> EnrichedDataRepo:
        return EnrichedDataRepo(
            dao=self.dao_container.enriched_data_dao,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ENRICHED_DATA_REPO
            ),
            user_id=self.config["db_user"]["id"],
            account_id=self.config["db_user"]["account_id"],
        )

    @property
    def trade_repo(self) -> TradeRepo:
        return TradeRepo(
            dao=self.dao_container.trade_dao,
            logger=self.logger_container.logger(logger_type=LoggerType.TRADE_REPO),
            user_id=self.config["db_user"]["id"],
            account_id=self.config["db_user"]["account_id"],
        )

    @property
    def order_repo(self) -> OrderRepo:
        return OrderRepo(
            dao=self.dao_container.order_dao,
            logger=self.logger_container.logger(logger_type=LoggerType.ORDER_REPO),
        )

    @property
    def watchlist_repo(self) -> WatchlistRepo:
        return WatchlistRepo(
            watchlist_path=self.config["backtester_paths"]["watchlist_path"],
            logger=self.logger_container.logger(logger_type=LoggerType.WATCHLIST_REPO),
        )

    def close(self):
        """Close resources like database connections."""
        self.db_container.close()
