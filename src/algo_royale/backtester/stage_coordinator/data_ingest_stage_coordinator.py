from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd
from alpaca.common.enums import SupportedCurrencies

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.column_names.data_ingest_columns import DataIngestColumns
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.services.market_data.alpaca_stock_service import AlpacaQuoteService


class DataIngestStageCoordinator(StageCoordinator):
    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        quote_service: AlpacaQuoteService,
        load_watchlist: Callable[[str], list[str]],
        watchlist_path_string: str,
    ):
        super().__init__(
            stage=BacktestStage.DATA_INGEST,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.load_watchlist = load_watchlist
        self.watchlist_path = watchlist_path_string
        self.quote_service = quote_service
        if not watchlist_path_string:
            raise ValueError("watchlist_path_string must be provided")
        if not self.get_watchlist():
            raise ValueError("Watchlist is empty")

    def get_watchlist(self):
        """
        Load the watchlist from the specified path.
        """
        return self.load_watchlist(self.watchlist_path)

    async def process(
        self,
        prepared_data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]],
    ) -> Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """
        Fetch data for all symbols and return as async iterators of DataFrames.
        The StageCoordinator._write method will handle saving.
        """
        result: Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]] = {}

        for symbol in self.get_watchlist():
            # Wrap the factory in a dict with None as the strategy name
            result[symbol] = {
                None: (lambda symbol=symbol: self._fetch_symbol_data(symbol=symbol))
            }
        return result

    async def _fetch_symbol_data(
        self,
        symbol: str,
    ) -> AsyncIterator[pd.DataFrame]:
        """
        Async generator that yields DataFrames for each page of fetched data for a symbol.
        No saving is done here; saving is handled by StageCoordinator._write.
        """
        page_token = None
        page_count = 0
        total_rows = 0

        self.logger.info(
            f"Fetching data for {symbol} from {self.start_date} to {self.end_date}"
        )

        try:
            while True:
                page_count += 1

                response = await self.quote_service.fetch_historical_bars(
                    symbols=[symbol],
                    start_date=self.start_date,
                    end_date=self.end_date,
                    currency=SupportedCurrencies.USD,
                    feed=DataFeed.IEX,
                    page_token=page_token,
                )

                if not response or not response.symbol_bars.get(symbol):
                    if page_count == 1:
                        self.logger.warning(f"No data returned for {symbol}")
                    break

                bars = response.symbol_bars[symbol]
                df = pd.DataFrame([bar.model_dump() for bar in bars])
                df[DataIngestColumns.SYMBOL] = symbol
                df = df.iloc[::-1].reset_index(drop=True)  # Reverse rows
                total_rows += len(df)
                yield df

                page_token = response.next_page_token
                if not page_token:
                    break

            self.logger.info(
                f"Finished fetching {symbol}: {page_count} pages, {total_rows} rows"
            )
        except Exception as e:
            self.logger.error(f"Error fetching {symbol}: {str(e)}")
            # Optionally: yield an empty DataFrame or handle error reporting here

        finally:
            await self.quote_service.client.aclose()
            self.logger.info(f"Closed connection for {symbol}")
