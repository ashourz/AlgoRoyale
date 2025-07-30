"""Manages the collection of available strategies and resolves them per symbol.
State of symbol-strategy pairs is maintained in the strategy registry.
Daily or on-demand update reports are generated to track changes in strategy availability and use.
"""

import json
from pathlib import Path
from typing import Dict

from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.logging.loggable import Loggable


class StrategyRegistry:
    def __init__(
        self,
        symbol_manager: SymbolManager,
        stage_data_manager: StageDataManager,
        evaluation_json_filename: str,
        viable_strategies_json_filename: str,
        logger: Loggable,
    ):
        self.symbol_manager = symbol_manager
        self.stage_data_manager = stage_data_manager
        self.evaluation_json_filename = evaluation_json_filename
        self.logger = logger
        self.state = {}

    def load_state(self):
        with open(self.config_path) as f:
            self.state = json.load(f)

    def get_strategies(self, symbol):
        return self.state.get(symbol, [])

    def write_report(self, filename, timestamp):
        report = {"timestamp": timestamp.isoformat(), "strategies": self.state}
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

    def _get_all_viable_strategies(self) -> Dict[str, Dict[str, float]]:
        """Get all viable strategies across all symbols."""
        all_strategies = {}
        try:
            for symbol in self.symbol_manager.get_symbols():
                strategies = self._get_viable_strategies(symbol)
                if strategies:
                    all_strategies[symbol] = strategies
        except Exception as e:
            self.logger.error(f"Error getting all viable strategies: {e}")
        return all_strategies

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
                return []

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
