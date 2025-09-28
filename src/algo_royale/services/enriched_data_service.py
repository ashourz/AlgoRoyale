from uuid import UUID

from algo_royale.logging.loggable import Loggable
from algo_royale.repo.enriched_data_repo import EnrichedDataRepo


class EnrichedDataService:
    def __init__(self, enriched_data_repo: EnrichedDataRepo, logger: Loggable):
        self.enriched_data_repo = enriched_data_repo
        self.logger = logger

    def insert_enriched_data(self, order_id: UUID, enriched_data: dict) -> UUID | None:
        try:
            result = self.enriched_data_repo.insert_enriched_data(
                str(order_id), enriched_data
            )
            self.logger.info(f"Inserted enriched data for order {order_id}: {result}")
            return result
        except Exception as e:
            self.logger.error(
                f"Error inserting enriched data for order {order_id}: {e}"
            )
            return None

    def fetch_enriched_data_by_order_id(self, order_id: UUID) -> list:
        try:
            result = self.enriched_data_repo.fetch_enriched_data_by_order_id(
                str(order_id)
            )
            self.logger.info(f"Fetched enriched data for order {order_id}: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error fetching enriched data for order {order_id}: {e}")
            return []

    def delete_all_enriched_data(self) -> int:
        try:
            result = self.enriched_data_repo.delete_all_enriched_data()
            self.logger.info(f"Deleted all enriched data: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error deleting all enriched data: {e}")
            return -1
