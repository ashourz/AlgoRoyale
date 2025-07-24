from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from algo_royale.backtester.stage_data.loader.portfolio_matrix_loader import (
    PortfolioMatrixLoader,
)


class PortfolioMatrixRepository:
    """
    Handles loading, saving, and caching of portfolio matrices for given symbols and date ranges.
    """

    def __init__(
        self, cache_dir: str, matrix_loader: PortfolioMatrixLoader, logger=None
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.matrix_loader = matrix_loader
        self.logger = logger

    def _get_cache_path(
        self, symbols: List[str], start_date: datetime, end_date: datetime
    ) -> Path:
        symbols_key = "_".join(sorted(symbols))
        fname = f"portfolio_matrix_{symbols_key}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.parquet"
        if self.logger:
            self.logger.debug(
                f"Cache path for portfolio matrix: {self.cache_dir / fname}"
            )
        return self.cache_dir / fname

    async def get_or_create_matrix(
        self, symbols: List[str], start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        cache_path = self._get_cache_path(symbols, start_date, end_date)
        if cache_path.exists():
            if self.logger:
                self.logger.info(f"Loading cached portfolio matrix from {cache_path}")
            return pd.read_parquet(cache_path)
        if self.logger:
            self.logger.info(
                f"No cached matrix found. Computing new portfolio matrix for {symbols} {start_date} to {end_date}"
            )
        matrix = await self.matrix_loader.get_portfolio_matrix(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
        )
        if matrix is not None and not matrix.empty:
            matrix.to_parquet(cache_path)
            if self.logger:
                self.logger.info(f"Saved new portfolio matrix to {cache_path}")
        return matrix
