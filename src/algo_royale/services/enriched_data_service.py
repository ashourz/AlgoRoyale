from algo_royale.logging.loggable import Loggable
from algo_royale.repo.enriched_data_repo import EnrichedDataRepo


class EnrichedDataService:
    def __init__(self, enriched_data_repo: EnrichedDataRepo, logger: Loggable):
        self.enriched_data_repo = enriched_data_repo
        self.logger = logger

    def insert_enriched_data(self, order_id: str, enriched_data: dict) -> int:
        try:
            result = self.enriched_data_repo.insert_enriched_data(
                order_id, enriched_data
            )
            self.logger.info(f"Inserted enriched data for order {order_id}: {result}")
            return result
        except Exception as e:
            self.logger.error(
                f"Error inserting enriched data for order {order_id}: {e}"
            )
            return -1

    def fetch_enriched_data_by_order_id(self, order_id: str) -> list:
        try:
            result = self.enriched_data_repo.fetch_enriched_data_by_order_id(order_id)
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
