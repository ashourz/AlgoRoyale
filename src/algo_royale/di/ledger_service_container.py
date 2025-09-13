from dependency_injector import containers, providers

from algo_royale.di.adapter_container import AdapterContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo_container import RepoContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.account_cash_service import AccountCashService
from algo_royale.services.clock_service import ClockService
from algo_royale.services.enriched_data_service import EnrichedDataService
from algo_royale.services.ledger_service import LedgerService
from algo_royale.services.orders_service import OrderService
from algo_royale.services.positions_service import PositionsService
from algo_royale.services.trades_service import TradesService


class LedgerServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    adapter_container: AdapterContainer = providers.DependenciesContainer()
    repo_container: RepoContainer = providers.DependenciesContainer()
    logger_container: LoggerContainer = providers.DependenciesContainer()
    clock_service: ClockService = providers.Dependency()

    account_cash_service = providers.Singleton(
        AccountCashService,
        cash_adapter=adapter_container.account_cash_adapter,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.ACCOUNT_CASH_SERVICE
        ),
    )

    enriched_data_service = providers.Singleton(
        EnrichedDataService,
        enriched_data_repo=adapter_container.enriched_data_repo,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.ENRICHED_DATA_SERVICE
        ),
    )

    order_service = providers.Singleton(
        OrderService,
        order_adapter=adapter_container.order_adapter,
        order_repo=repo_container.order_repo,
        trade_repo=repo_container.trades_repo,
        logger=logger_container.provides_logger(logger_type=LoggerType.ORDER_SERVICE),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    trades_service = providers.Singleton(
        TradesService,
        account_adapter=adapter_container.account_adapter,
        trade_repo=repo_container.trades_repo,
        logger=logger_container.provides_logger(logger_type=LoggerType.TRADE_SERVICE),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
        days_to_settle=config.tradeing.days_to_settle,
    )

    positions_service = providers.Singleton(
        PositionsService,
        positions_adapter=adapter_container.positions_adapter,
        trade_repo=repo_container.trades_repo,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.POSITION_SERVICE
        ),
        user_id=config.db.user.id,
        account_id=config.db.user.account_id,
    )

    ledger_service = providers.Singleton(
        LedgerService,
        cash_service=account_cash_service,
        order_service=order_service,
        trades_service=trades_service,
        position_service=positions_service,
        enriched_data_service=enriched_data_service,
        logger=logger_container.provides_logger(logger_type=LoggerType.LEDGER_SERVICE),
    )
