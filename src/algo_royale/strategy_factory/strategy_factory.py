import itertools
import json
from typing import Dict, List, Optional, Type

from algo_royale.strategy_factory.combinator.bollinger_bands_strategy_combinator import (
    BollingerBandsStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.combo_strategy_combinator import (
    ComboStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.macd_trailing_strategy_combinator import (
    MACDTrailingStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.mean_reversion_strategy_combinator import (
    MeanReversionStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.momentum_strategy_combinator import (
    MomentumStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.moving_average_crossover_strategy_combinator import (
    MovingAverageCrossoverStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.moving_average_strategy_combinator import (
    MovingAverageStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.pullback_entry_strategy_combinator import (
    PullbackEntryStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.rsi_strategy_combinator import (
    RSIStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.time_of_day_bias_strategy_combinator import (
    TimeOfDayBiasStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.trailing_stop_strategy_combinator import (
    TrailingStopStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.trend_scraper_strategy_combinator import (
    TrendScraperStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.volatility_breakout_strategy_combinator import (
    VolatilityBreakoutStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.volume_breakout_strategy_combinator import (
    VolumeBreakoutStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.vwap_reversion_strategy_combinator import (
    VWAPReversionStrategyCombinator,
)
from algo_royale.strategy_factory.combinator.wick_reversal_strategy_combinator import (
    WickReversalStrategyCombinator,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class StrategyFactory:
    """
    Factory for creating trading strategy instances from a JSON config file.
    - "defaults" strategies are applied to every symbol.
    - "symbols" can provide additional strategies for each symbol.
    - Strategy names in JSON are mapped to classes via strategy_map.
    """

    def __init__(
        self,
        strategy_map: Optional[Dict[str, Type]] = None,
    ):
        self.strategy_map = strategy_map
        self.all_strategy_combinations = self._get_all_strategy_combinations()

    def _get_merged_strategy_defs(self, symbol: str) -> List[dict]:
        default_strats = self.json_config.get("defaults", [])
        symbol_strats = self.json_config.get("symbols", {}).get(symbol, [])
        return default_strats + symbol_strats

    def create_strategies(
        self,
        json_path: str,
    ) -> Dict[str, List[object]]:
        """
        For each symbol in config, create all strategy instances (all param combos for param_grid).
        Returns dict: symbol -> list of strategy instances.
        """
        with open(json_path, "r") as f:
            self.json_config = json.load(f)

        strategies_per_symbol: Dict[str, List[object]] = {}
        all_symbols = list(self.json_config.get("symbols", {}).keys())
        for symbol in all_symbols:
            strat_defs = self._get_merged_strategy_defs(symbol)
            strategies = []
            for strat_def in strat_defs:
                name = strat_def.get("name")
                strat_cls = self.strategy_map.get(name)
                if strat_cls is None:
                    raise ValueError(f"Unknown strategy: {name}")
                param_grid = strat_def.get("param_grid")
                if param_grid:
                    param_names = list(param_grid.keys())
                    param_values = [
                        v if isinstance(v, list) else [v] for v in param_grid.values()
                    ]
                    for combo in itertools.product(*param_values):
                        params = dict(zip(param_names, combo))
                        strategies.append(strat_cls(**params))
                else:
                    params = strat_def.get("params", {})
                    strategies.append(strat_cls(**params))
            strategies_per_symbol[symbol] = strategies
        return strategies_per_symbol

    def _get_all_strategy_combinations() -> List[Strategy]:
        """
        Returns all strategy combinations across all symbols.
        This method is useful for testing or analysis purposes.
        """
        all_strategies = []
        all_strategies.extend(BollingerBandsStrategyCombinator.get_all_combinations())
        all_strategies.extend(ComboStrategyCombinator.get_all_combinations())
        all_strategies.extend(MACDTrailingStrategyCombinator.get_all_combinations())
        all_strategies.extend(MeanReversionStrategyCombinator.get_all_combinations())
        all_strategies.extend(MomentumStrategyCombinator.get_all_combinations())
        all_strategies.extend(
            MovingAverageCrossoverStrategyCombinator.get_all_combinations()
        )
        all_strategies.extend(MovingAverageStrategyCombinator.get_all_combinations())
        all_strategies.extend(PullbackEntryStrategyCombinator.get_all_combinations())
        all_strategies.extend(RSIStrategyCombinator.get_all_combinations())
        all_strategies.extend(TimeOfDayBiasStrategyCombinator.get_all_combinations())
        all_strategies.extend(TrailingStopStrategyCombinator.get_all_combinations())
        all_strategies.extend(TrendScraperStrategyCombinator.get_all_combinations())
        all_strategies.extend(
            VolatilityBreakoutStrategyCombinator.get_all_combinations()
        )
        all_strategies.extend(VolumeBreakoutStrategyCombinator.get_all_combinations())
        all_strategies.extend(VWAPReversionStrategyCombinator.get_all_combinations())
        all_strategies.extend(WickReversalStrategyCombinator.get_all_combinations())
        return all_strategies
