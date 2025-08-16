from algo_royale.clients.db.dao.base_dao import BaseDAO


class EnrichedDataDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_enriched_data_by_order_id(self, order_id: int) -> list:
        """
        Fetch enriched data for a specific order ID.
        :param order_id: The ID of the order to fetch enriched data for.
        :return: A list containing the enriched data, or an empty list if not found.
        """
        return self.fetch("get_enriched_data_by_order_id.sql", (order_id,))

    def insert_enriched_data(
        self,
        order_id: int,
        enriched_data: dict,
        user_id: str,
        account_id: str,
    ) -> int:
        """
        Insert enriched data for a specific order.
        :param order_id: The ID of the order to associate with the enriched data.
        :param enriched_data: A dictionary containing the enriched data.
        :param user_id: The ID of the user who owns the order.
        :param account_id: The ID of the account associated with the order.
        :return: The ID of the newly inserted enriched data, or -1 if the insertion failed.
        """
        # Prepare the values in the correct order as expected by the SQL file
        values = [order_id]
        # Add all expected enriched_data fields in the correct order
        enriched_fields = [
            "market_timestamp",
            "symbol",
            "market",
            "volume",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "num_trades",
            "volume_weighted_price",
            "pct_return",
            "log_return",
            "sma_10",
            "sma_20",
            "sma_50",
            "sma_100",
            "sma_150",
            "sma_200",
            "macd",
            "macd_signal",
            "rsi",
            "ema_9",
            "ema_10",
            "ema_12",
            "ema_20",
            "ema_26",
            "ema_50",
            "ema_100",
            "ema_150",
            "ema_200",
            "volatility_10",
            "volatility_20",
            "volatility_50",
            "atr_14",
            "hist_volatility_20",
            "range",
            "body",
            "upper_wick",
            "lower_wick",
            "vol_ma_10",
            "vol_ma_20",
            "vol_ma_50",
            "vol_ma_100",
            "vol_ma_200",
            "vol_change",
            "vwap_10",
            "vwap_20",
            "vwap_50",
            "vwap_100",
            "vwap_150",
            "vwap_200",
            "hour",
            "day_of_week",
            "adx",
            "momentum_10",
            "roc_10",
            "stochastic_k",
            "stochastic_d",
            "bollinger_upper",
            "bollinger_lower",
            "bollinger_width",
            "gap",
            "high_low_ratio",
            "obv",
            "adl",
        ]
        for field in enriched_fields:
            values.append(enriched_data.get(field))
        # Optionally add user_id and account_id if your table expects them
        values.extend([user_id, account_id])
        inserted_id = self.insert("insert_enriched_data.sql", tuple(values))
        if not inserted_id:
            self.logger.error(
                f"Failed to insert enriched data for order_id {order_id}."
            )
            return -1
        return inserted_id

    def delete_all_enriched_data(self) -> int:
        """
        Delete all enriched data from the database.
        :return: The number of rows deleted.
        """
        deleted_ids = self.execute("delete_all_enriched_data.sql")
        return len(deleted_ids) if deleted_ids else -1
