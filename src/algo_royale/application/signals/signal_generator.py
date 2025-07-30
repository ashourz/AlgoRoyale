from algo_royale.logging.loggable import Loggable


class SignalGenerator:
    def __init__(
        self,
        logger: Loggable,
    ):
        self.logger = logger
        self.symbols = []

    def update_symbols(self, symbols: list[str]):
        """
        Update the list of symbols to the provided list.
        """
        self.symbols = symbols

    def generate_signal(self, data):
        """
        Generate a trading signal based on the provided data and strategy.

        :param data: The market data to analyze.
        :return: A trading signal (buy, sell, hold).
        """
        return self.strategy.analyze(data)

    def _get_watchlist(self):
        """
        Load the watchlist from the specified path.
        """
        watchlist = self.data_loader.get_watchlist()
        if not watchlist or len(watchlist) == 0:
            raise ValueError(
                f"Watchlist loaded from {self.watchlist_path} is empty. Cannot proceed with data ingestion."
            )
        self.logger.info(
            f"Watchlist loaded with {len(watchlist)} symbols for stage: {self.stage}"
        )
        return watchlist
