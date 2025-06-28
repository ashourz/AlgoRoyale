"""
AssetMatrixPreparer: Utility for preparing feature-engineered data in the asset-matrix form

- Converts raw or feature-engineered DataFrames into the expected format for portfolio strategies:
    - Multi-symbol: index is timestamp, columns are asset symbols, values are features (e.g., returns, signals)
    - Single-symbol: returns the DataFrame as-is, with a single column
- Handles missing data and provides logging for shape/column issues
"""

import logging
from typing import Optional

import pandas as pd


class AssetMatrixPreparer:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def prepare(
        self,
        df: pd.DataFrame,
        symbol_col: str = "symbol",
        value_col: Optional[str] = None,
        timestamp_col: str = "timestamp",
    ) -> pd.DataFrame:
        """
        Prepares the DataFrame in asset-matrix form for portfolio strategies.
        Args:
            df: Input DataFrame (raw or feature-engineered)
            symbol_col: Name of the column containing asset symbols
            value_col: Name of the column containing the feature/values to pivot (if None, uses all columns except symbol/timestamp)
            timestamp_col: Name of the column containing timestamps
        Returns:
            pd.DataFrame: Asset-matrix DataFrame (index: timestamp, columns: symbols)
        """
        if symbol_col not in df.columns:
            self.logger.info(
                f"Single-symbol data detected (no '{symbol_col}' column). Returning as-is."
            )
            return df.set_index(timestamp_col) if timestamp_col in df.columns else df

        if value_col:
            pivot_df = df.pivot(
                index=timestamp_col, columns=symbol_col, values=value_col
            )
        else:
            # Use all columns except symbol/timestamp
            value_cols = [c for c in df.columns if c not in {symbol_col, timestamp_col}]
            if len(value_cols) == 1:
                pivot_df = df.pivot(
                    index=timestamp_col, columns=symbol_col, values=value_cols[0]
                )
            else:
                # Multi-feature: create MultiIndex columns
                pivot_df = df.pivot(
                    index=timestamp_col, columns=symbol_col, values=value_cols
                )

        self.logger.info(
            f"Asset-matrix shape: {pivot_df.shape}, columns: {pivot_df.columns}"
        )
        return pivot_df
