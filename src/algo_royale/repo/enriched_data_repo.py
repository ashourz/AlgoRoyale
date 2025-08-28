from uuid import UUID

from algo_royale.clients.db.dao.enriched_data_dao import EnrichedDataDAO
from algo_royale.logging.loggable import Loggable
from algo_royale.models.db.db_enriched_data import DBEnrichedData


class EnrichedDataRepo:
    def __init__(
        self, dao: EnrichedDataDAO, logger: Loggable, user_id: str, account_id: str
    ):
        self.dao = dao
        self.logger = logger
        self.user_id = user_id
        self.account_id = account_id

    def fetch_enriched_data_by_order_id(self, order_id: UUID) -> list[DBEnrichedData]:  # noqa: F821
        """
        Fetch enriched data for a specific order ID.
        :param order_id: The ID of the order to fetch enriched data for.
        :return: A list containing the enriched data, or an empty list if not found.
        """
        return self.dao.fetch_enriched_data_by_order_id(order_id)

    def insert_enriched_data(
        self,
        order_id: UUID,
        enriched_data: dict,
    ) -> int:
        """
        Insert enriched data for a specific order.
        :param order_id: The ID of the order to associate with the enriched data.
        :param enriched_data: A dictionary containing the enriched data.
        :return: The ID of the newly inserted enriched data, or -1 if the insertion failed.
        """
        return self.dao.insert_enriched_data(
            order_id, enriched_data, self.user_id, self.account_id
        )

    def delete_all_enriched_data(self) -> int:
        """
        Delete all enriched data from the database.
        :return: The number of rows deleted.
        """
        return self.dao.delete_all_enriched_data()
