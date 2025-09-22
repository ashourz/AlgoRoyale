from algo_royale.clients.db.dao.data_stream_session_dao import DataStreamSessionDAO
from algo_royale.clients.db.dao.enriched_data_dao import EnrichedDataDAO
from algo_royale.clients.db.dao.order_dao import OrderDAO
from algo_royale.clients.db.dao.trade_dao import TradeDAO
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.db_container import DBContainer
from algo_royale.logging.logger_type import LoggerType


class DAOContainer:
    """Data Access Object (DAO) Container"""

    def __init__(
        self, config, db_container: DBContainer, logger_container: LoggerContainer
    ):
        self.config = config
        self.db_container = db_container
        self.logger_container = logger_container

        self.sql_dir = self.config.db_paths.sql_dir

        self.data_stream_session_dao = DataStreamSessionDAO(
            connection=self.db_container.db_connection,
            sql_dir=self.sql_dir,
            logger=self.logger_container.logger(
                logger_type=LoggerType.DATA_STREAM_SESSION_DAO
            ),
        )

        self.enriched_data_dao = EnrichedDataDAO(
            connection=self.db_container.db_connection,
            sql_dir=self.sql_dir,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ENRICHED_DATA_DAO
            ),
        )

        self.trade_dao = TradeDAO(
            connection=self.db_container.db_connection,
            sql_dir=self.sql_dir,
            logger=self.logger_container.logger(logger_type=LoggerType.TRADE_DAO),
        )

        self.order_dao = OrderDAO(
            connection=self.db_container.db_connection,
            sql_dir=self.sql_dir,
            logger=self.logger_container.logger(logger_type=LoggerType.ORDER_DAO),
        )
