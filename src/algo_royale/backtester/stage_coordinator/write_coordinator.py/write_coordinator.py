from typing import AsyncIterator, Callable, Dict

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.enum.data_extension import DataExtension


class WriteCoordinator:
    """Coordinator for writing processed data to disk."""

    def __init__(self, data_writer, logger, start_date, end_date):
        self.data_writer = data_writer
        self.logger = logger
        self.start_date = start_date
        self.end_date = end_date

    async def write_symbol_strategy_data_factory(
        self,
        stage: BacktestStage,
        symbol_strategy_data_factory: Dict[
            str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ],
    ):
        """Write processed data to disk."""
        self.logger.info(f"Writing data for stage: {stage}")
        try:
            for symbol, strategy_factories in symbol_strategy_data_factory.items():
                await self._write_symbol_data(stage, symbol, strategy_factories)
        except Exception as e:
            self._handle_global_write_error(stage, e)
            return False

    async def _write_symbol_data(
        self,
        stage: BacktestStage,
        symbol: str,
        strategy_factories: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
    ):
        """Write data for a specific symbol."""
        try:
            self.logger.info(f"Writing data for symbol: {symbol} at stage: {stage}")
            for strategy_name, df_iter_factory in strategy_factories.items():
                await self._write_strategy_data(
                    stage, symbol, strategy_name, df_iter_factory
                )
        except Exception as e:
            self._handle_symbol_write_error(stage, symbol, e)

    async def _write_strategy_data(
        self,
        stage: BacktestStage,
        symbol: str,
        strategy_name: str,
        df_iter_factory: Callable[[], AsyncIterator[pd.DataFrame]],
    ):
        """Write data for a specific strategy."""
        try:
            if self.stage_data_manager.is_symbol_stage_done(
                stage, strategy_name, symbol, self.start_date, self.end_date
            ):
                self.logger.info(
                    f"Skipping {symbol} for stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date} (already marked as done)"
                )
                return

            self._clear_existing_data_if_needed(stage, strategy_name, symbol)

            gen = df_iter_factory()
            if not hasattr(gen, "__aiter__"):
                raise TypeError(f"Expected async iterator, got {type(gen)}")

            await self._write_pages(stage, strategy_name, symbol, gen)
            self.stage_data_manager.mark_symbol_stage(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                statusExtension=DataExtension.DONE,
                start_date=self.start_date,
                end_date=self.end_date,
            )
        except Exception as e:
            self._handle_strategy_write_error(stage, strategy_name, symbol, e)

    async def _write_pages(
        self,
        stage: BacktestStage,
        strategy_name: str,
        symbol: str,
        gen: AsyncIterator[pd.DataFrame],
    ):
        """Write pages of data for a strategy."""
        page_idx = 1
        async for df in gen:
            self.data_writer.save_stage_data(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                results_df=df,
                page_idx=page_idx,
                start_date=self.start_date,
                end_date=self.end_date,
            )
            page_idx += 1

    def _clear_existing_data_if_needed(
        self, stage: BacktestStage, strategy_name: str, symbol: str
    ):
        """Clear existing data if the directory is not marked as done."""
        out_dir = self.stage_data_manager.get_directory_path(
            stage, strategy_name, symbol, self.start_date, self.end_date
        )
        if out_dir.exists() and any(out_dir.iterdir()):
            self.logger.info(
                f"Clearing existing data for {symbol} at stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date}"
            )
            self.stage_data_manager.clear_directory(
                stage, strategy_name, symbol, self.start_date, self.end_date
            )

    def _handle_global_write_error(self, stage: BacktestStage, e: Exception):
        """Handle errors during the global write process."""
        self.logger.error(f"stage:{stage} data writing failed: {e}")
        self.stage_data_manager.write_error_file(
            stage=stage,
            strategy_name=None,
            symbol="",
            filename="write",
            error_message=f"stage:{stage} data writing failed: {e}",
            start_date=self.start_date,
            end_date=self.end_date,
        )

    def _handle_symbol_write_error(
        self, stage: BacktestStage, symbol: str, e: Exception
    ):
        """Handle errors during the symbol write process."""
        self.logger.error(f"stage:{stage} data writing failed for symbol {symbol}: {e}")
        self.stage_data_manager.write_error_file(
            stage=stage,
            strategy_name=None,
            symbol=symbol,
            filename="write",
            error_message=f"stage:{stage} data writing failed for symbol {symbol}: {e}",
            start_date=self.start_date,
            end_date=self.end_date,
        )

    def _handle_strategy_write_error(
        self, stage: BacktestStage, strategy_name: str, symbol: str, e: Exception
    ):
        """Handle errors during the strategy write process."""
        self.logger.error(
            f"stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date} data writing failed for symbol {symbol}: {e}"
        )
        self.stage_data_manager.write_error_file(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            filename="write",
            error_message=f"stage:{stage} | strategy:{strategy_name} data writing failed for symbol {symbol}: {e}",
            start_date=self.start_date,
            end_date=self.end_date,
        )
