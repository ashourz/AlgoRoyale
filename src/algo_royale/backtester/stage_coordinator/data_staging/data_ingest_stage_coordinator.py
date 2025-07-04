from datetime import datetime
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd
from alpaca.common.enums import SupportedCurrencies

from algo_royale.backtester.column_names.data_ingest_columns import DataIngestColumns
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.data_staging.symbol_strategy_data_writer import (
    SymbolStrategyDataWriter,
)
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.services.market_data.alpaca_stock_service import AlpacaQuoteService


class DataIngestStageCoordinator(StageCoordinator):
    def __init__(
        self,
        data_loader: StageDataLoader,
        data_writer: SymbolStrategyDataWriter,
        logger: Logger,
        quote_service: AlpacaQuoteService,
        load_watchlist: Callable[[str], list[str]],
        watchlist_path_string: str,
    ):
        super().__init__(
            stage_data_manager=stage_data_manager,
            data_writer=data_writer,
            logger=logger,
        )
        self.stage = BacktestStage.DATA_INGEST
        self.data_loader = data_loader
        self.data_writer = data_writer
        self.logger = logger
        self.quote_service = quote_service
        self.load_watchlist = load_watchlist
        self.watchlist_path = watchlist_path_string
        if not watchlist_path_string:
            raise ValueError("watchlist_path_string must be provided")

    async def run(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bool:
        """
        Orchestrate the stage: load, prepare, process, write.
        """
        self.logger.info(
            f"Starting stage: {self.stage} | start_date: {start_date} | end_date: {end_date}"
        )
        # Validate dates
        self.start_date = start_date
        self.end_date = end_date
        if not self.start_date or not self.end_date:
            self.logger.error(
                f"Start date and end date must be provided for stage: {self.stage}"
            )
            return False

        # Load the watchlist
        watchlist = self._get_watchlist()
        if not watchlist:
            self.logger.error(
                f"Watchlist is empty for stage: {self.stage}. Cannot proceed with data ingestion."
            )
            return False
        self.logger.info(
            f"Watchlist loaded with {len(watchlist)} symbols for stage: {self.stage}"
        )

        # Fetch data for all symbols in the watchlist
        watchlist_symbol_data = await self._fetch_watchlist_symbol_data(
            watchlist=watchlist
        )
        if not watchlist_symbol_data:
            self.logger.error(f"Data fetching failed for stage:{self.stage}")
            return False

        # Write watchlist symbol data to disk
        await self._write(
            stage=self.stage,
            processed_data=watchlist_symbol_data,
        )
        self.logger.info(f"stage:{self.stage} completed and files saved.")
        return True

    def _get_watchlist(self):
        """
        Load the watchlist from the specified path.
        """
        return self.data_loader.get_watchlist()

    async def _fetch_watchlist_symbol_data(
        self,
        watchlist: list[str],
    ) -> Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """
        Fetch data for all symbols and return as async iterators of DataFrames.
        The StageCoordinator._write method will handle saving.
        """
        result: Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]] = {}

        for symbol in watchlist:
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

            if total_rows == 0:
                self.logger.warning(
                    f"No data found for {symbol} in the specified date range."
                )

            self.logger.info(
                f"Finished fetching {symbol}: {page_count} pages, {total_rows} rows"
            )
        except Exception as e:
            self.logger.error(f"Error fetching {symbol}: {str(e)}")
            # Optionally: yield an empty DataFrame or handle error reporting here

        finally:
            await self.quote_service.client.aclose()
            self.logger.info(f"Closed connection for {symbol}")

    async def _write(
        self,
        stage: BacktestStage,
        processed_data: Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]],
    ):
        """Write processed data to disk."""
        return await self.data_writer.write_symbol_strategy_data_factory(
            stage=stage,
            symbol_strategy_data_factory=processed_data,
            start_data=self.start_data,
            end_data=self.end_data,
        )
