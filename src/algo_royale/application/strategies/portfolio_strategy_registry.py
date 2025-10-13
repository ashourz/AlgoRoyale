import json
import threading
from pathlib import Path
from typing import Dict, Sequence

# (removed unused import 'symbol')
from algo_royale.backtester.maps.portfolio_strategy_class_map import (
    PORTFOLIO_STRATEGY_CLASS_MAP,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy.portfolio.buffered_components.buffered_portfolio_strategy import (
    BufferedPortfolioStrategy,
)
from algo_royale.backtester.strategy_factory.portfolio.portfolio_strategy_factory import (
    PortfolioStrategyFactory,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.services.symbol_service import SymbolService


class PortfolioStrategyRegistry:
    def __init__(
        self,
        symbol_service: SymbolService,
        stage_data_manager: StageDataManager,
        strategy_summary_json_filename: str,
        viable_strategies_path: str,
        portfolio_strategy_factory: PortfolioStrategyFactory,
        optimization_root_path: str,
        logger: Loggable,
    ):
        self.symbol_manager = symbol_service
        self.stage_data_manager = stage_data_manager
        if not strategy_summary_json_filename:
            raise ValueError("strategy_summary_json_filename must be provided")
        self.strategy_summary_json_filename = strategy_summary_json_filename
        if not viable_strategies_path:
            raise ValueError("viable_strategies_path must be provided")
        self.viable_strategies_path = Path(viable_strategies_path)
        self.portfolio_strategy_factory = portfolio_strategy_factory
        self.logger = logger
        # Map of symbol_dir_name -> strategy descriptor dict (persisted as JSON)
        self.portfolio_strategy_map: dict[str, dict] = {}
        # Lock to protect concurrent access to portfolio_strategy_map and file writes
        self._lock = threading.RLock()
        self.optimization_root_path = Path(optimization_root_path)
        self._load_existing_viable_strategy_params()

    def get_buffered_portfolio_strategy(
        self, symbols: list[str]
    ) -> BufferedPortfolioStrategy | None:
        """Get the weighted buffer portfolio strategy for a given symbols"""
        try:
            self.logger.info(f"Getting portfolio strategy for {symbols}...")
            symbol_str = self._get_symbols_dir_name(symbols)
            # Acquire lock when reading shared in-memory map
            with self._lock:
                best_portfolio_strategy_map = self.portfolio_strategy_map.get(
                    symbol_str, {}
                )
            if not best_portfolio_strategy_map:
                self.logger.info(
                    f"No buffered strategies found for {symbol_str}. Retrieving existing viable strategies."
                )
                best_portfolio_strategy_map = self._update_portfolio_strategy_map(
                    symbols
                )
                # Only persist if we actually found a viable best strategy.
                if best_portfolio_strategy_map:
                    self._sync_viable_strategy_params()
                else:
                    self.logger.info(
                        f"No viable portfolio strategies found for {symbol_str}; skipping sync."
                    )

            return self._get_buffered_portfolio_strategy(best_portfolio_strategy_map)
        except Exception as e:
            self.logger.error(
                f"Error getting weighted buffer signal strategy for {symbols}: {e}"
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
                self.portfolio_strategy_map = {}
            with open(self.viable_strategies_path, "r") as f:
                try:
                    self.logger.info(
                        f"Loading viable strategies from {self.viable_strategies_path}..."
                    )
                    self.portfolio_strategy_map = json.load(f)
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Error decoding JSON from {self.viable_strategies_path}: {e}"
                    )
                    self.portfolio_strategy_map = {}
        except Exception as e:
            self.logger.error(f"Error getting existing strategies: {e}")

    def _sync_viable_strategy_params(self):
        """Sync the current state with the viable strategies file."""
        self.logger.info("Syncing viable portfolio strategy parameters...")
        try:
            # Write atomically: write to a temp file then replace the target.
            tmp_path = self.viable_strategies_path.with_suffix(".tmp")
            # Lock map snapshot during write to ensure consistency
            with self._lock:
                snapshot = dict(self.portfolio_strategy_map)
            with open(tmp_path, "w") as f:
                json.dump(snapshot, f, indent=2)
            # Use Path.replace/rename which is atomic on most OSes
            tmp_path.replace(self.viable_strategies_path)
            self.logger.info(
                f"Viable portfolio strategies successfully synced to {self.viable_strategies_path}"
            )
        except Exception as e:
            self.logger.error(f"Error syncing viable portfolio strategies: {e}")

    def _update_portfolio_strategy_map(self, symbols: list[str]) -> dict:
        try:
            symbol_str = self._get_symbols_dir_name(symbols)
            strategy_params = self._get_viable_strategies(symbols)

            # Choose the strategy with the highest viability_score. If strategy_params
            # is empty, return an empty dict.
            if not strategy_params:
                return {}

            # strategy_params is a dict: {strategy_name: {"viability_score": x, "params": {...}}}
            best_name, best_metrics = max(
                strategy_params.items(),
                key=lambda item: item[1].get("viability_score", float("-inf")),
            )

            best_strategy_dict = {
                "name": best_name,
                "viability_score": best_metrics.get("viability_score", 0),
                "params": best_metrics.get("params", {}),
            }

            self.logger.info(
                f"Best buffered strategy for {symbol_str}: {best_strategy_dict['name']} with viability score {best_strategy_dict['viability_score']}"
            )
            self.portfolio_strategy_map[symbol_str] = best_strategy_dict
            return best_strategy_dict
        except Exception as e:
            self.logger.error(
                f"Error getting best buffered strategies for {symbols}: {e}"
            )
        return {}

    def _get_buffered_portfolio_strategy(
        self, strategy_dict: dict
    ) -> BufferedPortfolioStrategy | None:
        """Get the buffered portfolio strategy for the given symbols."""
        try:
            if not strategy_dict:
                return None
            strategy_name = strategy_dict.get("name")
            params = strategy_dict.get("params", {})
            strategy_class = PORTFOLIO_STRATEGY_CLASS_MAP.get(strategy_name)
            if not strategy_class:
                self.logger.error(f"Unknown portfolio strategy: {strategy_name}")
                return None
            try:
                strategy_obj = self.portfolio_strategy_factory.build_buffered_strategy(
                    strategy_class=strategy_class, params=params
                )
                try:
                    self.logger.debug(
                        f"Successfully built buffered strategy for {strategy_name}: {strategy_obj.get_description()}"
                    )
                except Exception:
                    # Description call is best-effort for diagnostics
                    self.logger.debug(
                        f"Successfully built buffered strategy for {strategy_name}"
                    )
                return strategy_obj
            except Exception as e:
                self.logger.error(
                    f"Error building buffered strategy for {strategy_dict}: {e}"
                )
                return None
        except Exception as e:
            self.logger.error(
                f"Error building buffered strategy for {strategy_dict}: {e}"
            )
            return None

    def _get_viable_strategies(self, symbols: list[str]) -> Dict[str, Dict[str, float]]:
        """Get optimization results for a given strategy and symbol."""
        viable_strategy_params = {}
        try:
            symbol_dir = self._get_symbols_dir(symbols)
            # Only look for the portfolio summary file at the symbol directory
            symbol_summary = symbol_dir / self.strategy_summary_json_filename
            # Log the path we are checking so runtime can be diagnosed
            try:
                self.logger.info(
                    f"Checking for summary file for {symbols} at: {symbol_summary} (exists={symbol_summary.exists()})"
                )
            except Exception:
                # If symbol_dir isn't a Path for some reason, still log its repr
                self.logger.info(
                    f"Checking for summary file for {symbols} at: {repr(symbol_summary)}"
                )

            if not symbol_summary.exists():
                self.logger.warning(
                    f"No evaluation results found for {symbols} in {symbol_dir}. Skipping."
                )
                return {}

            try:
                self.logger.debug(
                    f"Found {self.strategy_summary_json_filename} for {symbols}: {symbol_summary}"
                )
                with open(symbol_summary) as f:
                    report = json.load(f)
                # Ensure strategy name is present (some outputs may omit it)
                if not report.get("strategy"):
                    report["strategy"] = report.get("strategy") or symbol_dir.name
                # If summary indicates viability, add to map
                if report.get("is_viable", False):
                    strategy_name = report.get("strategy")
                    viability_score = report.get("viability_score", 0)
                    params = report.get("most_common_best_params", {})
                    viable_strategy_params[strategy_name] = {
                        "viability_score": viability_score,
                        "params": params,
                    }
            except json.JSONDecodeError as e:
                self.logger.error(
                    f"Failed to decode JSON for {symbols} in {symbol_summary}: {e}"
                )
            except FileNotFoundError as e:
                self.logger.error(
                    f"Evaluation file not found for {symbols} in {symbol_summary}: {e}"
                )
            except Exception as e:
                self.logger.error(
                    f"Unexpected error processing summary for {symbols} in {symbol_summary}: {e}"
                )
            # Log the viable strategies found for easier runtime diagnosis
            try:
                self.logger.debug(
                    f"Viable strategies detected for {symbols}: {viable_strategy_params}"
                )
            except Exception:
                # Avoid logging failures causing selection failure
                pass
        except Exception as e:
            self.logger.error(f"Error getting viable strategies for {symbols}: {e}")
        return viable_strategy_params

    def _get_symbols_dir(
        self,
        symbols: list[str],
    ) -> Path:
        """Get the path to the optimization result JSON file for a given strategy and symbol."""
        symbol_str = self._get_symbols_dir_name(symbols)
        self.logger.debug(f"Getting symbols directory for {symbol_str}")
        out_dir = self.stage_data_manager.get_directory_path(
            base_dir=self.optimization_root_path, symbol=symbol_str
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def _get_symbols_dir_name(
        self,
        symbols: Sequence[str],
    ) -> str:
        return "_".join(sorted(symbols)) if symbols else "empty"
