import json
import itertools
from algo_royale.strategies.moving_average_strategy import MovingAverageStrategy

class StrategyFactory:
    """
    Factory for creating trading strategy instances for backtesting or live trading,
    supporting default strategies for all symbols, plus per-symbol overrides/additions.

    Config Structure Example
    -----------------------
    config = {
        "defaults": [
            {
                "name": "MovingAverageStrategy",
                "param_grid": {
                    "short_window": [10, 20],
                    "long_window": [50, 100]
                }
            }
        ],
        "symbols": {
            "AAPL": [
                {
                    "name": "MomentumStrategy",
                    "param_grid": {"window": [14, 28]}
                }
            ],
            "GOOG": []
        }
    }

    Usage
    -----
    # 1. Backtesting: Generate all parameter combinations per symbol/strategy
    factory = StrategyFactory()
    all_symbols = ["AAPL", "GOOG", "MSFT"]
    strategies = factory.create_backtest_strategies(config, all_symbols)
    # strategies["AAPL"] will be a list of all strategies (defaults + symbol-specific)

    # 2. Live Trading: Use fixed parameters for each symbol/strategy
    live_config = {
        "defaults": [
            {
                "name": "MovingAverageStrategy",
                "params": {
                    "short_window": 20,
                    "long_window": 100
                }
            }
        ],
        "symbols": {
            "AAPL": [
                {
                    "name": "MomentumStrategy",
                    "params": {"window": 28}
                }
            ]
        }
    }
    strategies = factory.create_live_strategies(live_config, all_symbols)

    # 3. Live Trading from file (e.g., best_strategies.json)
    # best_strategies.json:
    # {
    #   "AAPL": [
    #       {"name": "MovingAverageStrategy", "params": {"short_window": 20, "long_window": 100}}
    #   ],
    #   "GOOG": [
    #       {"name": "MovingAverageStrategy", "params": {"short_window": 10, "long_window": 100}}
    #   ]
    # }
    strategies = factory.create_live_strategies_from_file("best_strategies.json")

    Customization
    -------------
    To add more strategies:
        from algo_royale.strategies.momentum_strategy import MomentumStrategy
        factory = StrategyFactory(available_strategies={
            "MovingAverageStrategy": MovingAverageStrategy,
            "MomentumStrategy": MomentumStrategy,
        })

    Returns
    -------
    All methods return a dict:
        {
            "SYMBOL1": [strategy_instance1, strategy_instance2, ...],
            "SYMBOL2": [...],
            ...
        }
    """

    def __init__(self, available_strategies=None):
        if available_strategies is None:
            self.available_strategies = {
                "MovingAverageStrategy": MovingAverageStrategy,
                # "MomentumStrategy": MomentumStrategy
            }
        else:
            self.available_strategies = available_strategies

    def _get_merged_strategy_defs(self, symbol, config):
        """
        Merge defaults with symbol-specific strategies.
        Always includes defaults; adds any symbol-specific ones.
        """
        default_strats = config.get("defaults", [])
        symbol_strats = config.get("symbols", {}).get(symbol, [])
        return default_strats + symbol_strats

    def create_backtest_strategies(self, config, all_symbols):
        """
        Generate all parameter permutations for each symbol/strategy for backtesting.
        Parameters
        ----------
        config : dict
            Contains 'defaults' and 'symbols' keys.
        all_symbols : list of str
            All symbols to run backtests for.
        Returns
        -------
        dict
            Mapping of symbol -> list of strategy instances (all parameter combos).
        """
        strategies_per_symbol = {}
        for symbol in all_symbols:
            strat_defs = self._get_merged_strategy_defs(symbol, config)
            strategies = []
            for strat_def in strat_defs:
                name = strat_def.get("name")
                strat_cls = self.available_strategies.get(name)
                if strat_cls is None:
                    raise ValueError(f"Unknown strategy: {name}")
                param_grid = strat_def.get("param_grid", {})
                if not param_grid:
                    # If no grid (e.g., someone uses 'params' in backtest), just use as singleton
                    params = strat_def.get("params", {})
                    strategies.append(strat_cls(**params))
                else:
                    param_names = list(param_grid.keys())
                    param_values = list(param_grid.values())
                    for combo in itertools.product(*param_values):
                        params = dict(zip(param_names, combo))
                        strategies.append(strat_cls(**params))
            strategies_per_symbol[symbol] = strategies
        return strategies_per_symbol

    def create_live_strategies(self, config, all_symbols):
        """
        Create strategies for live trading with fixed parameters per symbol.
        Parameters
        ----------
        config : dict
            Contains 'defaults' and 'symbols' keys.
        all_symbols : list of str
            All symbols to use.
        Returns
        -------
        dict
            Mapping of symbol -> list of strategy instances (one per config).
        """
        strategies_per_symbol = {}
        for symbol in all_symbols:
            strat_defs = self._get_merged_strategy_defs(symbol, config)
            strategies = []
            for strat_def in strat_defs:
                name = strat_def.get("name")
                strat_cls = self.available_strategies.get(name)
                if strat_cls is None:
                    raise ValueError(f"Unknown strategy: {name}")
                params = strat_def.get("params", {})
                strategies.append(strat_cls(**params))
            strategies_per_symbol[symbol] = strategies
        return strategies_per_symbol

    def create_live_strategies_from_file(self, filename):
        """
        Load live strategies from a JSON file containing the best strategies and parameters per symbol.
        Parameters
        ----------
        filename : str
            Path to the JSON file. The file should map symbol to a list of strategy dicts.
        Returns
        -------
        dict
            Mapping of symbol -> list of strategy instances.
        """
        with open(filename, "r") as f:
            symbol_strategies = json.load(f)
        strategies_per_symbol = {}
        for symbol, strat_defs in symbol_strategies.items():
            strategies = []
            for strat_def in strat_defs:
                name = strat_def.get("name")
                params = strat_def.get("params", {})
                strat_cls = self.available_strategies.get(name)
                if strat_cls is None:
                    raise ValueError(f"Unknown strategy: {name}")
                strategies.append(strat_cls(**params))
            strategies_per_symbol[symbol] = strategies
        return strategies_per_symbol