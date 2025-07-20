import json
from logging import Logger
from pathlib import Path
from typing import Any, Optional

from algo_royale.backtester.maps.strategy_class_map import SYMBOL_STRATEGY_CLASS_MAP
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy_factory.signal.strategy_factory import (
    StrategyFactory,
)


class SymbolStrategyManager:
    def __init__(
        self,
        base_dir: str,
        stage_data_manager: StageDataManager,
        symbol_strategy_evaluation_filename: str = "evaluation_result.json",
        logger: Logger = None,
    ):
        """
        Args:
            base_dir: Base directory for stage data (used by stage_data_manager).
            strategy_class_registry: Mapping from strategy class name (str) to class type.
            stage_data_manager: Object responsible for resolving symbol directory paths.
            logger: Optional logger for debug/info/warning messages.
        """
        self.base_dir = Path(base_dir)
        self.stage_data_manager = stage_data_manager
        self.symbol_strategy_evaluation_filename = symbol_strategy_evaluation_filename
        self.logger = (logger,)

    def get_optimized_strategy(self, symbol: str) -> Optional[Any]:
        """
        Uses stage_data_manager to resolve the symbol directory, loads evaluation_result.json, checks viability, and returns an initialized strategy instance or None.
        Logs key events if logger is provided.
        """
        symbol_dir = self.stage_data_manager.get_directory_path(
            base_dir=self.base_dir, symbol=symbol
        )
        eval_file = Path(symbol_dir) / self.symbol_strategy_evaluation_filename
        if not eval_file.exists():
            if self.logger:
                self.logger.warning(
                    f"Evaluation file not found for symbol: {symbol} at {eval_file}"
                )
            return None
        try:
            with open(eval_file, "r") as f:
                data = json.load(f)
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to load evaluation file for symbol {symbol}: {e}"
                )
            return None
        best_params = data.get("most_common_best_params")
        is_viable = data.get("is_viable", False)
        if not best_params or not is_viable:
            if self.logger:
                self.logger.info(
                    f"Symbol {symbol} is not viable or missing best_params."
                )
            return None
        strat_name = None
        params = None
        if "stateful_logic" in best_params and best_params["stateful_logic"]:
            strat_name, params = next(iter(best_params["stateful_logic"].items()))
        elif "entry_conditions" in best_params and best_params["entry_conditions"]:
            entry = best_params["entry_conditions"][0]
            strat_name, params = next(iter(entry.items()))
        if not strat_name:
            if self.logger:
                self.logger.warning(
                    f"No strategy class name found for symbol {symbol}."
                )
            return None
        strat_class = SYMBOL_STRATEGY_CLASS_MAP.get(strat_name)
        if not strat_class:
            if self.logger:
                self.logger.error(
                    f"Strategy class '{strat_name}' not found in SYMBOL_STRATEGY_CLASS_MAP for symbol {symbol}."
                )
            return None
        if self.logger:
            self.logger.debug(
                f"Instantiating strategy '{strat_name}' for symbol {symbol} with params: {params} using StrategyFactory.build_strategy"
            )
        return StrategyFactory.build_strategy(strat_class, params)
