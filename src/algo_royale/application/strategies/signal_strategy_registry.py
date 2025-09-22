"""Manages the collection of available strategies and resolves them per symbol.
State of symbol-strategy pairs is maintained in the strategy registry.
Daily or on-demand update reports are generated to track changes in strategy availability and use.
"""

import json
from pathlib import Path
from typing import Dict

from algo_royale.backtester.maps.strategy_class_map import SYMBOL_STRATEGY_CLASS_MAP
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy.signal.combined_weighted_signal_strategy import (
    CombinedWeightedSignalStrategy,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_factory import (
    SignalStrategyFactory,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.services.symbol_service import SymbolService


class SignalStrategyRegistry:
    def __init__(
        self,
        symbol_service: SymbolService,
        stage_data_manager: StageDataManager,
        evaluation_json_filename: str,
        viable_strategies_path: str,
        signal_strategy_factory: SignalStrategyFactory,
        logger: Loggable,
        combined_buy_threshold: float = 0.5,
        combined_sell_threshold: float = 0.5,
    ):
        self.symbol_manager = symbol_service
        self.stage_data_manager = stage_data_manager
        self.evaluation_json_filename = evaluation_json_filename
        self.viable_strategies_path = Path(viable_strategies_path)
        self.signal_strategy_factory = signal_strategy_factory
        self.logger = logger
        self.combined_buy_threshold = combined_buy_threshold
        if not (0 <= self.combined_buy_threshold <= 1):
            raise ValueError("combined_buy_threshold must be between 0 and 1")
        self.combined_sell_threshold = combined_sell_threshold
        if not (0 <= self.combined_sell_threshold <= 1):
            raise ValueError("combined_sell_threshold must be between 0 and 1")
        self.symbol_strategy_map = {}
        self._load_existing_viable_strategy_params()

    def get_combined_weighted_signal_strategy(
        self, symbol: str
    ) -> CombinedWeightedSignalStrategy | None:
        """Get the weighted buffer signal strategy for a given symbol."""
        try:
            self.logger.info(f"Getting weighted buffer signal strategy for {symbol}...")
            viable_symbol_strategy_map = self.symbol_strategy_map.get(symbol, {})
            if not viable_symbol_strategy_map:
                self.logger.info(
                    f"No buffered strategies found for {symbol}. Retrieving existing viable strategies."
                )
                viable_symbol_strategy_map = self._update_symbol_strategy_map(symbol)
                self._sync_viable_strategy_params()
            return self._get_combined_weighted_signal_strategy(
                viable_symbol_strategy_map
            )
        except Exception as e:
            self.logger.error(
                f"Error getting weighted buffer signal strategy for {symbol}: {e}"
            )
        return None

    def _load_existing_viable_strategy_params(self):
        """Get existing viable strategy parameters for a given symbol."""
        self.logger.info("Retrieving viable strategy parameters...")
        try:
            if (
                not self.viable_strategies_path.exists()
                or self.viable_strategies_path.stat().st_size == 0
            ):
                self.logger.info(
                    f"Viable strategies file {self.viable_strategies_path} does not exist or is empty. Initializing."
                )
                with open(self.viable_strategies_path, "w") as f:
                    json.dump({}, f)
                self.symbol_strategy_map = {}
            with open(self.viable_strategies_path, "r") as f:
                try:
                    self.symbol_strategy_map = json.load(f)
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Error decoding JSON from {self.viable_strategies_path}: {e}"
                    )
                    self.symbol_strategy_map = {}
        except Exception as e:
            self.logger.error(f"Error getting existing strategies: {e}")

    def _sync_viable_strategy_params(self):
        """Sync the current state with the viable strategies file."""
        self.logger.info("Syncing viable strategy parameters...")
        try:
            with open(self.viable_strategies_path, "w") as f:
                json.dump(self.symbol_strategy_map, f, indent=2)
            self.logger.info(
                f"Viable strategies successfully synced to {self.viable_strategies_path}"
            )
        except Exception as e:
            self.logger.error(f"Error syncing viable strategies: {e}")

    def _update_symbol_strategy_map(self, symbol: str) -> dict:
        """Update the symbol strategy map with viable strategies."""
        self.logger.info(f"Getting all buffered strategies for {symbol}...")
        try:
            strategy_params = self._get_viable_strategies(symbol)
            self.symbol_strategy_map[symbol] = {}
            for strategy_name, metrics in strategy_params.items():
                viability_score = metrics.get("viability_score", 0)
                params = metrics.get("params", {})
                self.symbol_strategy_map[symbol][strategy_name] = {
                    "viability_score": viability_score,
                    "params": params,
                }
            return self.symbol_strategy_map[symbol]
        except Exception as e:
            self.logger.error(f"Error getting all strategies: {e}")
        return None

    def _get_combined_weighted_signal_strategy(
        self, viable_strategies: dict
    ) -> CombinedWeightedSignalStrategy | None:
        try:
            all_buffered_strategies = {}
            for strategy_name, metrics in viable_strategies.items():
                viability_score = metrics.get("viability_score", 0)
                params = metrics.get("params", {})
                strategy_class = SYMBOL_STRATEGY_CLASS_MAP.get(strategy_name)
                if not strategy_class:
                    self.logger.error(f"Unknown strategy class for {strategy_name}")
                    continue
                buffered_strategy = (
                    self.signal_strategy_factory.build_buffered_strategy(
                        strategy_class=strategy_class,
                        params=params,
                    )
                )
                all_buffered_strategies[buffered_strategy] = viability_score
            if not all_buffered_strategies:
                self.logger.warning(
                    f"No buffered strategies found for {viable_strategies}"
                )
                return None
            return CombinedWeightedSignalStrategy(
                buffered_strategies=all_buffered_strategies,
                buy_threshold=self.combined_buy_threshold,
                sell_threshold=self.combined_sell_threshold,
            )
        except Exception as e:
            self.logger.error(f"Error getting combined weighted signal strategy: {e}")
        return None

    def _get_viable_strategies(self, symbol: str) -> Dict[str, Dict[str, float]]:
        """Get optimization results for a given strategy and symbol."""
        viable_strategy_params = {}
        try:
            symbol_dir = self._get_symbol_dir(symbol)
            strategy_dirs = [d for d in symbol_dir.iterdir() if d.is_dir()]
            reports = []
            for strat_dir in strategy_dirs:
                try:
                    self.logger.debug(f"Checking strategy directory: {strat_dir}")
                    eval_path = strat_dir / self.evaluation_json_filename
                    if eval_path.exists():
                        with open(eval_path) as f:
                            loaded_results = json.load(f)
                        if not self._validate_input_report(loaded_results):
                            self.logger.warning(
                                f"Invalid evaluation report for {symbol} in {strat_dir}. Skipping."
                            )
                            continue
                        report = loaded_results
                        report["strategy"] = strat_dir.name
                        reports.append(report)
                except Exception as e:
                    self.logger.error(
                        f"Error processing strategy directory {strat_dir}: {e}"
                    )

            if not reports:
                self.logger.warning(
                    f"No evaluation results found for {symbol} in {symbol_dir}. Skipping."
                )
                return {}

            # Filter only viable strategies
            for report in reports:
                try:
                    if report.get("is_viable", False):
                        strategy_name = report["strategy"]
                        viability_score = report.get("viability_score", 0)
                        params = report.get("most_common_best_params", {})
                        metrics = {
                            "viability_score": viability_score,
                            "params": params,
                        }
                        viable_strategy_params[strategy_name] = metrics
                except KeyError as e:
                    self.logger.error(
                        f"Missing expected key in report for {symbol}: {e}"
                    )
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Failed to decode JSON for {symbol} in {strat_dir}: {e}"
                    )
                except FileNotFoundError as e:
                    self.logger.error(
                        f"Evaluation file not found for {symbol} in {strat_dir}: {e}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Unexpected error processing report for {symbol} in {strat_dir}: {e}"
                    )

        except Exception as e:
            self.logger.error(f"Error getting viable strategies for {symbol}: {e}")
        return viable_strategy_params

    def _get_symbol_dir(
        self,
        symbol: str,
    ) -> Path:
        """Get the path to the optimization result JSON file for a given strategy and symbol."""
        out_dir = self.stage_data_manager.get_directory_path(
            base_dir=self.optimization_root, symbol=symbol
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir


# Usage example:
# registry = StrategyRegistry("strategies.json")
# registry.load_state()
# registry.write_report("start_of_day_report.json", datetime.now())
