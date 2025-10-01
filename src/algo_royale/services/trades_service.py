## service\trade_service.py
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from algo_royale.adapters.trading.account_adapter import AccountAdapter
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_account import AccountActivity
from algo_royale.models.alpaca_trading.enums.enums import ActivityType
from algo_royale.models.db.db_trade import DBTrade
from algo_royale.repo.trade_repo import TradeRepo
from algo_royale.services.clock_service import ClockService


class TradesService:
    def __init__(
        self,
        account_adapter: AccountAdapter,
        trade_repo: TradeRepo,
        clock_service: ClockService,
        logger: Loggable,
        user_id: str,
        account_id: str,
        days_to_settle: int = 1,
    ):
        self.repo = trade_repo
        self.account_adapter = account_adapter
        self.clock_service = clock_service
        self.logger = logger
        self.user_id = user_id
        self.account_id = account_id
        self.days_to_settle = days_to_settle

    def fetch_trades_by_order_id(self, order_id: UUID) -> list[DBTrade]:
        """Fetch trades by their associated order ID."""
        return self.repo.fetch_trades_by_order_id(order_id)

    def fetch_unsettled_trades(self, limit: int = 100, offset: int = 0) -> list:
        """Fetch all unsettled trades with pagination.
        :param limit: Maximum number of trades to fetch.
        :param offset: Offset for pagination.
        :return: List of unsettled trades.
        """
        return self.repo.fetch_unsettled_trades(limit, offset)

    def update_settled_trades(self):
        """Update settlement status for all trades."""
        try:
            self.logger.info("Updating settled trades...")
            settlement_datetime = self.clock_service.now()
            updated_count = self.repo.update_settled_trades(settlement_datetime)
            if updated_count < 0:
                self.logger.error(
                    f"Failed to update settled trades | update count: {updated_count}"
                )
                return
            self.logger.info(f"Updated {updated_count} settled trades.")
        except Exception as e:
            self.logger.error(f"Error updating settled trades: {e}")

    def insert_trade(
        self,
        symbol: str,
        action: str,
        price: Decimal,
        quantity: int,
        executed_at: datetime,
        order_id: UUID,
    ) -> UUID | None:
        """Insert a new trade record.
        :param symbol: The stock symbol of the trade.
        :param action: The action of the trade (e.g., 'buy', 'sell').
        :param price: The price at which the trade was executed.
        :param quantity: The number of shares traded.
        :param executed_at: The time when the trade was executed.
        :param order_id: The ID of the associated order.
        :return: The ID of the newly inserted trade record.
        """
        settlement_date = self._get_settlement_date(executed_at)
        return self.repo.insert_trade(
            symbol=symbol,
            action=action,
            settlement_date=settlement_date,
            price=price,
            quantity=quantity,
            executed_at=executed_at,
            order_id=order_id,
        )

    def fetch_trades_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> list:
        """Fetch trades within a specific date range.
        :param start_date: The start date of the range.
        :param end_date: The end date of the range.
        :param limit: The maximum number of trades to return.
        :param offset: The number of trades to skip.
        :return: A list of trades within the specified date range.
        """
        return self.repo.fetch_trades_by_date_range(start_date, end_date, limit, offset)

    def delete_trade(self, trade_id: UUID) -> int:
        """Delete a trade record.
        :param trade_id: The ID of the trade to delete.
        :return: Number of deleted records."""
        return self.repo.delete_trade(trade_id)

    def delete_all_trades(self) -> int:
        """Delete all trade records.
        This is a destructive operation and should be used with caution.
        :return: Number of deleted records.
        """
        return self.repo.delete_all_trades()

    def _fetch_all_local_trades_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[DBTrade]:
        """Fetch all local trades from the repository."""
        all_trades = []
        limit = 100
        fetch = True
        offset = 0

        while fetch:
            trades = self.repo.fetch_trades_by_date_range(
                start_date, end_date, limit, offset
            )
            all_trades.extend(trades)
            if len(trades) < limit:
                fetch = False
            else:
                offset += limit

        return all_trades

    def _trade_key(self, trade: DBTrade) -> tuple:
        return (
            trade.symbol,
            trade.action,
            trade.settled,
            trade.settlement_date,
            trade.price,
            trade.quantity,
            trade.executed_at,
            trade.order_id,
        )

    async def reconcile_trades(
        self, start_date: datetime, end_date: datetime, rerun: bool = True
    ):
        """Reconcile trades between the local database and the Alpaca API."""
        try:
            local_trades = self._fetch_all_local_trades_by_date_range(
                start_date, end_date
            )
            account_activities = (
                await self.account_adapter.get_account_activities_by_activity_type(
                    activity_type=ActivityType.FILL, after=start_date, until=end_date
                )
            )
            account_trades = [
                self._account_activity_to_dbtrade(activity)
                for activity in account_activities.activities
                if activity is not None
            ]
            # Filter out None values
            account_trades = [t for t in account_trades if t is not None]
            # Build dicts for O(1) lookup
            local_trade_dict = {self._trade_key(trade): trade for trade in local_trades}
            account_trade_dict = {
                self._trade_key(trade): trade for trade in account_trades
            }

            # Find duplicates in local trades
            duplicate_trades = self._find_duplicate_local_trades(local_trades)
            added_trades = []
            removed_trades = []

            for trade in duplicate_trades:
                self.logger.info(f"Found duplicate trade: {trade.id}")
                self._remove_trade(trade)
                removed_trades.append(trade)

            # Remove local trades not present in account trades
            for key, trade in local_trade_dict.items():
                if key not in account_trade_dict:
                    self.logger.info(
                        f"Trade {trade.id} is not present in account trades."
                    )
                    self._remove_trade(trade)
                    removed_trades.append(trade)

            # Add account trades not present in local trades
            for key, trade in account_trade_dict.items():
                if key not in local_trade_dict:
                    self.logger.info(
                        f"Trade {trade.id} is not present in local trades."
                    )
                    self._insert_trade(trade)
                    added_trades.append(trade)

            if rerun:
                await self.reconcile_trades(start_date, end_date, rerun=False)
            else:
                is_same_length = self._validate_trade_list_length(
                    account_trades, local_trades
                )
                if not is_same_length:
                    self.logger.warning(
                        "Trade lists are not of the same length after reconciliation."
                    )
                if added_trades:
                    self.logger.warning(
                        f"Post reconciliation added trades: {len(added_trades)}"
                    )
                if removed_trades:
                    self.logger.warning(
                        f"Post reconciliation removed trades: {len(removed_trades)}"
                    )
        except Exception as e:
            self.logger.error(f"Error during trade reconciliation: {e}")

    def _remove_trade(self, trade: DBTrade) -> int:
        """Remove a trade from the local database."""
        try:
            removed_count = self.repo.delete_trade(trade.id)
            if removed_count == -1:
                self.logger.error(f"Failed to remove trade: {trade}")
                return -1
            self.logger.info(f"Removed trade with ID: {trade.id}")
            return removed_count
        except Exception as e:
            self.logger.error(f"Error during trade removal: {e}")
            return -1

    def _insert_trade(self, trade: DBTrade) -> int:
        """Insert a trade into the local database."""
        try:
            trade_id = self.repo.insert_trade(
                external_id=trade.external_id,
                symbol=trade.symbol,
                action=trade.action,
                settlement_date=trade.settlement_date,
                price=trade.price,
                quantity=trade.quantity,
                executed_at=trade.executed_at,
                order_id=trade.order_id,
            )
            if trade_id is None or trade_id == -1:
                self.logger.error(f"Failed to insert trade: {trade}")
                return -1
            self.logger.info(f"Inserted trade with ID: {trade_id}")
            return trade_id
        except Exception as e:
            self.logger.error(f"Error during trade insertion: {e}")
            return -1

    def _validate_trade_list_length(
        self, account_list: list[DBTrade], local_list: list[DBTrade]
    ) -> bool:
        """Check if the trade lists are of equal length."""
        try:
            diff = len(account_list) - len(local_list)
            if diff > 0:
                self.logger.warning(f"Account trade list is longer by {diff} trades.")
            if diff < 0:
                self.logger.warning(f"Local trade list is longer by {-diff} trades.")
            return diff == 0
        except Exception as e:
            self.logger.error(f"Error during trade list length validation: {e}")
            return False

    def _find_duplicate_local_trades(
        self, local_trades: list[DBTrade]
    ) -> list[DBTrade]:
        try:
            seen = set()
            duplicates = []
            for trade in local_trades:
                key = self._trade_key(trade)
                if key in seen:
                    duplicates.append(trade)
                else:
                    seen.add(key)
            return duplicates
        except Exception as e:
            self.logger.error(f"Error finding duplicate local trades: {e}")
            return []

    def _get_settlement_date(self, execution_time: datetime) -> datetime | None:
        """Calculate the settlement date based on the execution time."""
        try:
            if not execution_time:
                self.logger.error(
                    "Execution time is None, cannot calculate settlement date."
                )
                return None
            settlement_date = execution_time + timedelta(days=self.days_to_settle)
            ## Correct settlement date to start of day
            settlement_date = settlement_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            self.logger.debug(
                f"Calculated settlement date: {settlement_date} for execution time: {execution_time}"
            )
            return settlement_date
        except Exception as e:
            self.logger.error(f"Error calculating settlement date: {e}")
            return None

    def _account_activity_to_dbtrade(self, activity: AccountActivity) -> DBTrade | None:
        try:
            now = self.clock_service.now()
            settlement_date = self._get_settlement_date(activity.transaction_time)
            isSettled = True if settlement_date and settlement_date <= now else False
            if activity is None:
                self.logger.error(
                    "Account activity is None, cannot convert to DBTrade."
                )
                return None
            if not activity.id:
                self.logger.error(
                    f"Account activity ID is None, cannot convert to DBTrade. Activity: {activity}"
                )
                return None
            return DBTrade(
                id=uuid4(),
                external_id=activity.id,
                symbol=activity.symbol,
                action=activity.side,
                settled=isSettled,
                settlement_date=settlement_date,
                price=float(activity.price),
                quantity=int(activity.qty),
                executed_at=activity.transaction_time,
                created_at=now,
                updated_at=now,
                order_id=activity.order_id,
                user_id=self.user_id,
                account_id=self.account_id,
            )
        except Exception as e:
            self.logger.error(f"Error converting account activity to DBTrade: {e}")
            return None
