from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

import dateutil
import pandas as pd
from alpaca.common.enums import SupportedCurrencies

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.pipeline.data_manage.stage_data_loader import (
    StageDataLoader,
)
from algo_royale.backtester.pipeline.data_manage.stage_data_manager import (
    StageDataManager,
)
from algo_royale.backtester.pipeline.data_manage.stage_data_writer import (
    StageDataWriter,
)
from algo_royale.backtester.pipeline.data_preparer.async_data_preparer import (
    AsyncDataPreparer,
)
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.watchlist.watchlist import load_watchlist
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.services.market_data.alpaca_stock_service import AlpacaQuoteService


class DataIngestStageCoordinator(StageCoordinator):
    def __init__(
        self,
        config: dict,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        pipeline_data_manager: StageDataManager,
        logger: Logger,
        quote_service: AlpacaQuoteService,
    ):
        super().__init__(
            stage=BacktestStage.DATA_INGEST,
            config=config,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            pipeline_data_manager=pipeline_data_manager,
            logger=logger,
        )
        watchlist_path_string = config.get("paths.backtester", "watchlist_path")
        start_date = config.get("backtest", "start_date")
        end_date = config.get("backtest", "end_date")

        if not start_date or not end_date:
            raise ValueError("Start date or end date not specified in config")
        if not watchlist_path_string:
            raise ValueError("Watchlist path not specified in config")

        self.watchlist = load_watchlist(watchlist_path_string)
        self.start_date = dateutil.parser.parse(start_date)
        self.end_date = dateutil.parser.parse(end_date)

        if not self.watchlist:
            raise ValueError("Watchlist is empty")

        self.quote_service = quote_service

    async def process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """
        Fetch data for all symbols and return as async iterators of DataFrames.
        The StageCoordinator._write method will handle saving.
        """
        result: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]] = {}

        for symbol in self.watchlist:
            result[symbol] = lambda symbol=symbol: self._fetch_symbol_data(symbol)
        return result

    async def _fetch_symbol_data(self, symbol: str) -> AsyncIterator[pd.DataFrame]:
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
                df["symbol"] = symbol
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
