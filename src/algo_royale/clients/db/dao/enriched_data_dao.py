from uuid import UUID

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.models.db.db_enriched_data import DBEnrichedData


class EnrichedDataDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_enriched_data_by_order_id(self, order_id: UUID) -> list[DBEnrichedData]:
        """
        Fetch enriched data for a specific order ID.
        :param order_id: The ID of the order to fetch enriched data for.
        :return: A list containing the enriched data, or an empty list if not found.
        """
        rows = self.fetch("fetch_enriched_data_by_order_id.sql", (str(order_id),))
        if not rows:
            self.logger.warning(f"No enriched data found for order_id {order_id}.")
            return []
        return [DBEnrichedData.from_tuple(row) for row in rows]

    def insert_enriched_data(
        self,
        order_id: UUID,
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
        values = [
            str(order_id)
        ]  # Add all expected enriched_data fields in the correct order
        enriched_fields = DBEnrichedData.columns()[2:]  # Skip 'id' and 'order_id'

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
        delete_count = self.execute("delete_all_enriched_data.sql")
        return delete_count or -1
