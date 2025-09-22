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
        self.db_container = DBContainer(
            config=self.config,
            secrets=self.secrets,
            logger_container=self.logger_container,
        )

        self.dao_container = DAOContainer(
            config=self.config,
            db_container=self.db_container,
            logger_container=self.logger_container,
        )

        self.data_stream_session_repo = DataStreamSessionRepo(
            dao=self.dao_container.data_stream_session_dao,
            logger=self.logger_container.logger(
                logger_type=LoggerType.DATA_STREAM_SESSION_REPO
            ),
            user_id=self.config.db_user.id,
            account_id=self.config.db_user.account_id,
        )

        self.enriched_data_repo = EnrichedDataRepo(
            dao=self.dao_container.enriched_data_dao,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ENRICHED_DATA_REPO
            ),
            user_id=self.config.db_user.id,
            account_id=self.config.db_user.account_id,
        )

        self.trade_repo = TradeRepo(
            dao=self.dao_container.trade_dao,
            logger=self.logger_container.logger(logger_type=LoggerType.TRADE_REPO),
            user_id=self.config.db_user.id,
            account_id=self.config.db_user.account_id,
        )

        self.order_repo = OrderRepo(
            dao=self.dao_container.order_dao,
            logger=self.logger_container.logger(logger_type=LoggerType.ORDER_REPO),
            user_id=self.config.db_user.id,
            account_id=self.config.db_user.account_id,
        )

        self.watchlist_repo = WatchlistRepo(
            watchlist_path=self.config.backtester_paths.watchlist_path,
            logger=self.logger_container.logger(logger_type=LoggerType.WATCHLIST_REPO),
        )
