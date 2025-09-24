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

        shared_connection = self.db_container.db_connection

        self.data_stream_session_dao = DataStreamSessionDAO(
            connection=shared_connection,
            sql_dir=self.config["db_paths"]["sql_dir_data_stream_session"],
            logger=self.logger_container.logger(
                logger_type=LoggerType.DATA_STREAM_SESSION_DAO
            ),
        )

        self.enriched_data_dao = EnrichedDataDAO(
            connection=shared_connection,
            sql_dir=self.config["db_paths"]["sql_dir_enriched_data"],
            logger=self.logger_container.logger(
                logger_type=LoggerType.ENRICHED_DATA_DAO
            ),
        )

        self.trade_dao = TradeDAO(
            connection=shared_connection,
            sql_dir=self.config["db_paths"]["sql_dir_trades"],
            logger=self.logger_container.logger(logger_type=LoggerType.TRADE_DAO),
        )

        self.order_dao = OrderDAO(
            connection=shared_connection,
            sql_dir=self.config["db_paths"]["sql_dir_orders"],
            logger=self.logger_container.logger(logger_type=LoggerType.ORDER_DAO),
        )
