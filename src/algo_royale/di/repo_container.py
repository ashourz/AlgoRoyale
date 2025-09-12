from dependency_injector import containers, providers

from algo_royale.di.dao_container import DAOContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.repo.data_stream_session_repo import DataStreamSessionRepo
from algo_royale.repo.enriched_data_repo import EnrichedDataRepo
from algo_royale.repo.order_repo import OrderRepo
from algo_royale.repo.trade_repo import TradeRepo
from algo_royale.repo.watchlist_repo import WatchlistRepo


class RepoContainer(containers.DeclarativeContainer):
    """Repository Container"""

    config: providers.Configuration = providers.Configuration()
    dao: DAOContainer = providers.DependenciesContainer()
    logger_container: LoggerContainer = providers.Singleton()

    data_stream_session_repo = providers.Singleton(
        DataStreamSessionRepo,
        dao=dao.data_stream_session_dao,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.DATA_STREAM_SESSION_REPO
        ),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    enriched_data_repo = providers.Singleton(
        EnrichedDataRepo,
        dao=dao.enriched_data_dao,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.ENRICHED_DATA_REPO
        ),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    trade_repo = providers.Singleton(
        TradeRepo,
        dao=dao.trade_dao,
        logger=logger_container.provides_logger(logger_type=LoggerType.TRADE_REPO),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    order_repo = providers.Singleton(
        OrderRepo,
        dao=dao.order_dao,
        logger=logger_container.provides_logger(logger_type=LoggerType.ORDER_REPO),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    watchlist_repo = providers.Singleton(
        WatchlistRepo,
        watchlist_path=config.backtester.paths.watchlist_path,
        logger=logger_container.provides_logger(logger_type=LoggerType.WATCHLIST_REPO),
    )
