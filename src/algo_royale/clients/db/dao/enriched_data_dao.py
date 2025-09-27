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

    def insert_enriched_data(self, order_id: UUID, enriched_data: dict) -> int:
        """
        Insert enriched data for a specific order.
        :param order_id: The ID of the order to associate with the enriched data.
        :param enriched_data: A dictionary containing the enriched data.
        :return: The ID of the newly inserted enriched data, or -1 if the insertion failed.
        """
        # Prepare the values in the correct order as expected by the SQL file
        # Use all columns except 'id' (which is auto-incremented)
        self.logger.debug(f"Inserting enriched data for order_id {order_id}.")
        enriched_fields = DBEnrichedData.columns()[1:]  # Skip only 'id'
        values = []
        for field in enriched_fields:
            if field == "order_id":
                values.append(str(order_id))
            else:
                values.append(enriched_data.get(field))
        sql_query = self._load_sql("insert_enriched_data.sql")
        num_placeholders = sql_query.count("%s")
        self.logger.debug(f"SQL Query: {sql_query}")
        self.logger.debug(f"Number of %s placeholders: {num_placeholders}")
        self.logger.debug(f"Enriched fields: {enriched_fields}")
        self.logger.debug(f"Values count: {len(values)}")
        self.logger.debug(f"Values: {values}")
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
        delete_count = self.delete("delete_all_enriched_data.sql")
        return delete_count or -1
