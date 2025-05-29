import itertools
import json
from typing import Dict, List, Optional, Type


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
