## service\trade_service.py
from datetime import datetime, timedelta
from decimal import Decimal

from algo_royale.adapters.trading.account_adapter import AccountAdapter
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_account import AccountActivity
from algo_royale.models.alpaca_trading.enums.enums import ActivityType
from algo_royale.models.db.db_trade import DBTrade
from algo_royale.repo.trade_repo import TradeEntry, TradeRepo


class TradesService:
    def __init__(
        self,
        account_adapter: AccountAdapter,
        repo: TradeRepo,
        logger: Loggable,
        user_id: str,
        account_id: str,
        days_to_settle: int = 1,
    ):
        self.repo = repo
        self.account_adapter = account_adapter
        self.logger = logger
        self.user_id = user_id
        self.account_id = account_id

    def get_unsettled_trades(self, limit: int = 100, offset: int = 0) -> list:
        """Fetch all unsettled trades with pagination.
        :param limit: Maximum number of trades to fetch.
        :param offset: Offset for pagination.
        :return: List of unsettled trades.
        """
        return self.repo.fetch_unsettled_trades(limit, offset)

    def insert_trade(
        self,
        symbol: str,
        market: str,
        action: str,
        settlement_date: datetime,
        entry_price: Decimal,
        exit_price: Decimal,
        shares: int,
        entry_time: datetime,
        exit_time: datetime,
        notes: str,
        order_id: int,
    ) -> int:
        """Insert a new trade record.
        :param symbol: The stock symbol of the trade.
        :param market: The market where the trade occurred (e.g., 'NYSE', 'NASDAQ').
        :param action: The action of the trade (e.g., 'buy', 'sell').
        :param settlement_date: The settlement date of the trade.
        :param entry_price: The entry price of the trade.
        :param exit_price: The exit price of the trade.
        :param shares: The number of shares traded.
        :param entry_time: The time when the trade was entered.
        :param exit_time: The time when the trade was exited.
        :param notes: Additional notes about the trade.
        :param order_id: The ID of the associated order.
        :return: The ID of the newly inserted trade record.
        """
        return self.repo.insert_trade(
            symbol,
            market,
            action,
            settlement_date,
            entry_price,
            exit_price,
            shares,
            entry_time,
            exit_time,
            notes,
            order_id,
            self.user_id,
            self.account_id,
        )

    def get_trades_by_date_range(
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

    def update_trade_as_settled(self, trade_id: int) -> int:
        """Update a trade as settled."""
        return self.repo.update_trade_as_settled(trade_id)

    def delete_trade(self, trade_id: int) -> int:
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

    def get_trades(self, limit: int = None, offset: int = 0) -> list:
        """Get trades with pagination."""
        ## TODO: Not Yet Implemented
        raise NotImplementedError("This method is not yet implemented.")

    def add_trade(self, trade):
        """Add a new trade record."""
        ## TODO: Not Yet Implemented
        raise NotImplementedError("This method is not yet implemented.")

    def update_trade(self, trade_id, updated_trade):
        """Update an existing trade record."""
        ## TODO: Not Yet Implemented
        raise NotImplementedError("This method is not yet implemented.")

    def _get_trade_pnl(self, trade_entry: TradeEntry) -> Decimal:
        """Calculate the profit or loss of a trade."""
        ## TODO: Not Yet Implemented
        raise NotImplementedError("This method is not yet implemented.")

    def _get_all_local_trades_by_date_range(
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
            if len(trades) < limit:
                fetch = False
            else:
                all_trades.extend(trades)
                offset += limit

        return all_trades

    async def reconcile_trades(self, start_date: datetime, end_date: datetime):
        """Reconcile trades between the local database and the Alpaca API."""
        local_trades = self._get_all_local_trades_by_date_range(start_date, end_date)
        account_activities = (
            await self.account_adapter.get_account_activities_by_activity_type(
                activity_type=ActivityType.FILL, after=start_date, until=end_date
            )
        )
        order_ids = []

        for activity in account_activities.activities:
            if activity.order_id is not None:
                order_ids.append(activity.order_id)

        for trade in local_trades:
            order_ids.append(trade.order_id)

        for order_id in order_ids:
            self.logger.info(f"Reconciliation for order ID: {order_id}")
            order_activities = [
                activity
                for activity in account_activities.activities
                if activity.order_id == order_id
            ]
            order_local_trades = [
                trade for trade in local_trades if trade.order_id == order_id
            ]

            trade_times = []
            for activity in order_activities:
                if activity.transaction_time is not None:
                    trade_times.append(activity.transaction_time)

            for trade in order_local_trades:
                trade_times.append(trade.executed_at)

            for time in trade_times:
                self.logger.info(f"Trade time: {time}")
                activities = [
                    activity
                    for activity in order_activities
                    if activity.transaction_time == time
                ]
                local_trades = [
                    trade for trade in order_local_trades if trade.executed_at == time
                ]

                if not activities and not local_trades:
                    self.logger.warning(
                        f"No activities or local trades found for time: {time}"
                    )
                    continue

    def _get_settlement_date(self, execution_time: datetime) -> datetime | None:
        """Calculate the settlement date based on the execution time."""
        if not execution_time:
            self.logger.warning(
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

    def _account_activity_to_dbtrade(self, activity: AccountActivity) -> DBTrade:
        now = datetime.now()
        settlement_date = self._get_settlement_date(activity.transaction_time)
        isSettled = True if settlement_date and settlement_date <= now else False
        return DBTrade(
            symbol=activity.symbol,
            action=activity.side,
            settled=isSettled,
            settlement_date=settlement_date,
            price=float(activity.price),
            quantity=int(activity.qty),
            executed_at=activity.transaction_time,
            order_id=activity.order_id,
            user_id=self.user_id,
            account_id=self.account_id,
        )
