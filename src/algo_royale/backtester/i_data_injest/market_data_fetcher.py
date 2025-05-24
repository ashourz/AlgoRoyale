import asyncio
from logging import Logger
from pathlib import Path
from typing import Optional

import dateutil.parser
import pandas as pd
from alpaca.common.enums import SupportedCurrencies
from alpaca.data.enums import DataFeed

from algo_royale.backtester.pipeline.data_manage.data_extension import DataExtension
from algo_royale.backtester.pipeline.data_manage.pipeline_data_manager import (
    PipelineDataManager,
)
from algo_royale.backtester.pipeline.data_manage.pipeline_stage import PipelineStage
from algo_royale.backtester.watchlist.watchlist import load_watchlist
from algo_royale.config.config import Config
from algo_royale.services.market_data.alpaca_stock_service import AlpacaQuoteService


class MarketDataFetcher:
    def __init__(
        self,
        config: Config,
        logger: Logger,
        quote_service: AlpacaQuoteService,
        pipeline_data_manager: PipelineDataManager,
    ):
        try:
            # Initialize directories and services
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

            # Ensure watchlist is not empty
            if not self.watchlist:
                raise ValueError("Watchlist is empty")

            self.quote_service = quote_service

            self.pipeline_data_manager = pipeline_data_manager
            self.pipeline_stage = PipelineStage.DATA_INGEST

            # Initialize logger
            self.logger = logger
            self.logger.info("MarketDataFetcher initialized")

        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MarketDataFetcher: {e}")

    def _get_data_ingest_symbol_dir(self, symbol: str) -> Path:
        """Get the directory for a symbol in the data ingest stage"""
        return self.pipeline_data_manager.get_directory_path(
            stage=self.pipeline_stage, symbol=symbol
        )

    async def fetch_all(self) -> None:
        """Fetch data for all symbols in the watchlist"""
        self.logger.info("Starting async data fetching")
        tasks = []
        for symbol in self.watchlist:
            symbol_dir = self._get_data_ingest_symbol_dir(symbol=symbol)
            if not self._has_existing_data(symbol_dir):
                tasks.append(self._fetch_and_save_symbol(symbol))

        if tasks:
            self.logger.info(f"Fetching data for {len(tasks)} symbols...")
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for symbol, success in zip(self.watchlist, results):
                if isinstance(success, Exception):
                    self.logger.error(f"Failed to fetch {symbol}: {str(success)}")
                elif not success:
                    self.logger.error(f"Failed to fetch {symbol} (unknown error)")

    def _has_existing_data(self, symbol_dir: Path) -> bool:
        """Check if valid data exists for a symbol"""
        if not symbol_dir.exists():
            return False
        return any(symbol_dir.iterdir())

    async def _fetch_and_save_symbol(self, symbol: str) -> bool:
        """Fetch and save data for a symbol, returning success status"""
        symbol_dir = self._get_data_ingest_symbol_dir(symbol=symbol)
        symbol_dir.mkdir(exist_ok=True)

        page_count = 0  # Initialize page_count to avoid unbound error
        page_path: Optional[Path] = None  # Initialize page_path to avoid unbound error
        try:
            page_token = None
            total_rows = 0

            self.logger.info(
                f"Fetching data for {symbol} from {self.start_date} to {self.end_date}"
            )

            while True:
                page_count += 1
                page_name = f"{symbol}_page_{page_count}"
                page_path = symbol_dir / page_name + ".csv"

                # Fetch data from API
                response = await self.quote_service.fetch_historical_bars(
                    symbols=[symbol],
                    start_date=self.start_date,
                    end_date=self.end_date,
                    currency=SupportedCurrencies.USD,
                    feed=DataFeed.IEX,
                    page_token=page_token,
                )

                # Check response
                if not response or not response.symbol_bars.get(symbol):
                    if page_count == 1:
                        self.pipeline_data_manager.write_error_file(
                            stage=self.pipeline_stage,
                            strategy_name=None,
                            symbol=symbol,
                            filename=f"{page_name}.error",
                            error_message=f"No data returned for {symbol}",
                        )
                        self.logger.warning(f"No data returned for {symbol}")
                        return False
                    break

                # Process and save page
                bars = response.symbol_bars[symbol]
                df = pd.DataFrame([bar.model_dump() for bar in bars])
                df["symbol"] = symbol
                total_rows += len(df)

                await asyncio.to_thread(df.to_csv, page_path, index=False)

                self.logger.info(
                    f"Saved page {page_count} for {symbol} with {len(df)} rows"
                )

                # Check for more pages
                page_token = response.next_page_token
                if not page_token:
                    break

            self.logger.info(
                f"Finished fetching {symbol}: {page_count} pages, {total_rows} rows"
            )
            # Mark the symbol stage as done
            self.pipeline_data_manager.mark_symbol_stage(
                stage=self.pipeline_stage,
                symbol=symbol,
                statusExtension=DataExtension.DONE,
            )
            return True

        except Exception as e:
            self.logger.error(f"Error fetching {symbol}: {str(e)}")
            # Handle specific exceptions if needed
            self.pipeline_data_manager.write_error_file(
                stage=self.pipeline_stage,
                strategy_name=None,
                symbol=symbol,
                filename="fetch_and_save_symbol",
                error_message=f"Error fetching {symbol}: {str(e)}",
            )
            # Clean up partial data
            if page_count == 1 and page_path and page_path.exists():
                page_path.unlink()
            return False
        finally:
            await self.quote_service.client.aclose()
