from dependency_injector import containers, providers

from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.dao_container import DAOContainer
from algo_royale.di.repo.db_container import DBContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.repo.data_stream_session_repo import DataStreamSessionRepo
from algo_royale.repo.enriched_data_repo import EnrichedDataRepo
from algo_royale.repo.order_repo import OrderRepo
from algo_royale.repo.trade_repo import TradeRepo
from algo_royale.repo.watchlist_repo import WatchlistRepo


class RepoContainer(containers.DeclarativeContainer):
    """Repository Container"""

    config: providers.Configuration = providers.Configuration()
    secrets: providers.Configuration = providers.Configuration()
    logger_container: LoggerContainer = providers.Singleton()
    db_container = providers.Container(
        DBContainer,
        config=config,
        secrets=secrets,
        logger_container=logger_container,
    )

    dao_container = providers.Container(
        DAOContainer,
        config=config,
        db_container=db_container,
        logger_container=logger_container,
    )

    data_stream_session_repo = providers.Singleton(
        DataStreamSessionRepo,
        dao=dao_container.data_stream_session_dao,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.DATA_STREAM_SESSION_REPO
        ),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    enriched_data_repo = providers.Singleton(
        EnrichedDataRepo,
        dao=dao_container.enriched_data_dao,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.ENRICHED_DATA_REPO
        ),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    trade_repo = providers.Singleton(
        TradeRepo,
        dao=dao_container.trade_dao,
        logger=logger_container.provides_logger(logger_type=LoggerType.TRADE_REPO),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    order_repo = providers.Singleton(
        OrderRepo,
        dao=dao_container.order_dao,
        logger=logger_container.provides_logger(logger_type=LoggerType.ORDER_REPO),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    watchlist_repo = providers.Singleton(
        WatchlistRepo,
        watchlist_path=config.backtester.paths.watchlist_path,
        logger=logger_container.provides_logger(logger_type=LoggerType.WATCHLIST_REPO),
    )
