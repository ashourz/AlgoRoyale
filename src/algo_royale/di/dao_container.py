from dependency_injector import containers, providers

from algo_royale.clients.db.dao.data_stream_session_dao import DataStreamSessionDAO
from algo_royale.clients.db.dao.enriched_data_dao import EnrichedDataDAO
from algo_royale.clients.db.dao.order_dao import OrderDAO
from algo_royale.clients.db.dao.trade_dao import TradeDAO
from algo_royale.di.db_container import DBContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType


class DAOContainer(containers.DeclarativeContainer):
    """Data Access Object (DAO) Container"""

    config: providers.Configuration = providers.Configuration()
    db_container: DBContainer = providers.DependenciesContainer()
    logger_container: LoggerContainer = providers.DependenciesContainer()
    sql_dir = config.db.paths.sql_dir
    data_stream_session_dao = providers.Singleton(
        DataStreamSessionDAO,
        connection=db_container.db_connection,
        sql_dir=sql_dir,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.DATA_STREAM_SESSION_DAO
        ),
    )

    enriched_data_dao = providers.Singleton(
        EnrichedDataDAO,
        connection=db_container.db_connection,
        sql_dir=sql_dir,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.ENRICHED_DATA_DAO
        ),
    )

    trade_dao = providers.Singleton(
        TradeDAO,
        connection=db_container.db_connection,
        sql_dir=sql_dir,
        logger=logger_container.provides_logger(logger_type=LoggerType.TRADE_DAO),
    )

    order_dao = providers.Singleton(
        OrderDAO,
        connection=db_container.db_connection,
        sql_dir=sql_dir,
        logger=logger_container.provides_logger(logger_type=LoggerType.ORDER_DAO),
    )
