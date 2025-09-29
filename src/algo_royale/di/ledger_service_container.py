from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.account_cash_service import AccountCashService
from algo_royale.services.enriched_data_service import EnrichedDataService
from algo_royale.services.ledger_service import LedgerService
from algo_royale.services.orders_service import OrderService
from algo_royale.services.positions_service import PositionsService
from algo_royale.services.symbol_service import SymbolService
from algo_royale.services.trades_service import TradesService


# Refactored to a regular class
class LedgerServiceContainer:
    def __init__(
        self, config, adapter_container, repo_container, logger_container, clock_service
    ):
        self.config = config
        self.adapter_container = adapter_container
        self.repo_container = repo_container
        self.logger_container = logger_container
        self.clock_service = clock_service

    @property
    def account_cash_service(self) -> AccountCashService:
        return AccountCashService(
            cash_adapter=self.adapter_container.account_cash_adapter,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ACCOUNT_CASH_SERVICE
            ),
        )

    @property
    def enriched_data_service(self) -> EnrichedDataService:
        return EnrichedDataService(
            enriched_data_repo=self.repo_container.enriched_data_repo,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ENRICHED_DATA_SERVICE
            ),
        )

    @property
    def order_service(self) -> OrderService:
        return OrderService(
            orders_adapter=self.adapter_container.orders_adapter,
            order_repo=self.repo_container.order_repo,
            trade_repo=self.repo_container.trade_repo,
            logger=self.logger_container.logger(logger_type=LoggerType.ORDER_SERVICE),
        )

    @property
    def trades_service(self) -> TradesService:
        return TradesService(
            account_adapter=self.adapter_container.account_adapter,
            trade_repo=self.repo_container.trade_repo,
            logger=self.logger_container.logger(logger_type=LoggerType.TRADE_SERVICE),
            user_id=self.config["db_user"]["id"],
            account_id=self.config["db_user"]["account_id"],
            days_to_settle=int(self.config["trading"]["days_to_settle"]),
        )

    @property
    def positions_service(self) -> PositionsService:
        return PositionsService(
            positions_adapter=self.adapter_container.positions_adapter,
            trade_repo=self.repo_container.trade_repo,
            logger=self.logger_container.logger(
                logger_type=LoggerType.POSITION_SERVICE
            ),
            user_id=self.config["db_user"]["id"],
            account_id=self.config["db_user"]["account_id"],
        )

    @property
    def ledger_service(self) -> LedgerService:
        return LedgerService(
            cash_service=self.account_cash_service,
            order_service=self.order_service,
            trades_service=self.trades_service,
            position_service=self.positions_service,
            enriched_data_service=self.enriched_data_service,
            logger=self.logger_container.logger(logger_type=LoggerType.LEDGER_SERVICE),
        )

    @property
    def symbol_service(self) -> SymbolService:
        return SymbolService(
            watchlist_repo=self.repo_container.watchlist_repo,
            positions_service=self.positions_service,
            logger=self.logger_container.logger(logger_type=LoggerType.SYMBOL_SERVICE),
        )
