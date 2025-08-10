import json
from pathlib import Path
from typing import Dict, Sequence

from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.backtester.evaluator import symbol
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy.portfolio.buffered_components.buffered_portfolio_strategy import (
    BufferedPortfolioStrategy,
)
from algo_royale.backtester.strategy_factory.portfolio.portfolio_strategy_factory import (
    PortfolioStrategyFactory,
)
from algo_royale.logging.loggable import Loggable


class PortfolioStrategyRegistry:
    def __init__(
        self,
        symbol_manager: SymbolManager,
        stage_data_manager: StageDataManager,
        evaluation_json_filename: str,
        viable_strategies_path: str,
        portfolio_strategy_factory: PortfolioStrategyFactory,
        logger: Loggable,
    ):
        self.symbol_manager = symbol_manager
        self.stage_data_manager = stage_data_manager
        self.evaluation_json_filename = evaluation_json_filename
        self.viable_strategies_path = Path(viable_strategies_path)
        self.portfolio_strategy_factory = portfolio_strategy_factory
        self.logger = logger
        self.portfolio_strategy_map: dict[list[str], BufferedPortfolioStrategy] = {}
        self._load_existing_viable_strategy_params()

    def get_buffered_portfolio_strategy(
        self, symbols: list[str]
    ) -> BufferedPortfolioStrategy | None:
        """Get the weighted buffer portfolio strategy for a given symbols"""
        try:
            self.logger.info(f"Getting portfolio strategy for {symbols}...")
            portfolio_strategy = self.portfolio_strategy_map.get(symbols, {})
            if not portfolio_strategy:
                self.logger.info(
                    f"No buffered strategies found for {symbol}. Retrieving existing viable strategies."
                )
                portfolio_strategy = self._get_weighted_buffered_strategies(symbol)
                self.portfolio_strategy_map[symbol] = portfolio_strategy
                self._sync_viable_strategy_params()
            return self.portfolio_strategy_factory.build_buffered_strategy(
                strategy_class=portfolio_strategy_class, params=params
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
                self.portfolio_strategy_map = {}
            with open(self.viable_strategies_path, "r") as f:
                try:
                    ##TODO: this is incorrect
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
            with open(self.viable_strategies_path, "w") as f:
                json.dump(self.portfolio_strategy_map, f, indent=2)
            self.logger.info(
                f"Viable portfolio strategies successfully synced to {self.viable_strategies_path}"
            )
        except Exception as e:
            self.logger.error(f"Error syncing viable portfolio strategies: {e}")

    def _get_best_buffered_strategies(
        self, symbol: str
    ) -> Dict[BufferedPortfolioStrategy, float]:
        """Get all buffered strategies for a given symbol."""
        self.logger.info(f"Getting all buffered strategies for {symbol}...")
        best_strategy: BufferedPortfolioStrategy | None = None
        best_viability_score: float = 0
        try:
            strategy_params = self._get_viable_strategies(symbol)
            for strategy_name, metrics in strategy_params.items():
                viability_score = metrics.get("viability_score", 0)
                if viability_score > best_viability_score:
                    best_viability_score = viability_score
                    best_strategy = (
                        self.portfolio_strategy_factory.build_buffered_strategy(
                            strategy_class=strategy_name,
                            params=metrics.get("params", {}),
                        )
                    )
            if best_strategy:
                self.logger.info(
                    f"Best buffered strategy for {symbol}: {best_strategy}"
                )
                return best_strategy
            else:
                self.logger.warning(f"No viable buffered strategy found for {symbol}")
                return None
        except Exception as e:
            self.logger.error(
                f"Error getting best buffered strategies for {symbol}: {e}"
            )
        return None

    def _get_viable_strategies(self, symbols: list[str]) -> Dict[str, Dict[str, float]]:
        """Get optimization results for a given strategy and symbol."""
        viable_strategy_params = {}
        try:
            symbol_dir = self._get_symbols_dir(symbols)
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
                                f"Invalid evaluation report for {symbols} in {strat_dir}. Skipping."
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
                    f"No evaluation results found for {symbols} in {symbol_dir}. Skipping."
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
                        f"Missing expected key in report for {symbols}: {e}"
                    )
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Failed to decode JSON for {symbols} in {strat_dir}: {e}"
                    )
                except FileNotFoundError as e:
                    self.logger.error(
                        f"Evaluation file not found for {symbols} in {strat_dir}: {e}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Unexpected error processing report for {symbols} in {strat_dir}: {e}"
                    )

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
            base_dir=self.optimization_root, symbol=symbol_str
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def _get_symbols_dir_name(
        self,
        symbols: Sequence[str],
    ) -> str:
        return "_".join(sorted(symbols)) if symbols else "empty"
