from typing import Callable, List, Optional

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


class TrendScraperStrategy(Strategy):
    """
    Trend Scraper Strategy with flexible trend confirmation and exit conditions.

    Buy when all trend and entry functions return True.
    Sell when any exit function returns True.
    Hold otherwise.
    """

    def __init__(
        self,
        filters: Optional[List[StrategyFilter]] = None,
        trend_funcs: Optional[List[Callable[[pd.DataFrame], pd.Series]]] = None,
        entry_funcs: Optional[List[Callable[[pd.DataFrame], pd.Series]]] = None,
        exit_funcs: Optional[List[Callable[[pd.DataFrame], pd.Series]]] = None,
    ):
        """
        Parameters:
        - filters: List of StrategyFilter objects for pre-filtering.
        - trend_funcs: List of trend confirmation functions (should return boolean Series).
        - entry_funcs: List of entry condition functions (should return boolean Series).
        - exit_funcs: List of exit condition functions (should return boolean Series).
        """
        super().__init__(
            filters=filters,
            trend_funcs=trend_funcs,
            entry_funcs=entry_funcs,
            exit_funcs=exit_funcs,
        )
