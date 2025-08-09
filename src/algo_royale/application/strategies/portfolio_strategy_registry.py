from algo_royale.application.symbol.symbol_manager import SymbolManager
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
        self.viable_strategies_path = viable_strategies_path
        self.portfolio_strategy_factory = portfolio_strategy_factory
        self.logger = logger
        self.buffered_portfolio_strategy_map: dict[
            list[str], BufferedPortfolioStrategy
        ] = {}

    def get_buffered_portfolio_strategy(
        self, symbols: list[str]
    ) -> BufferedPortfolioStrategy | None:
        if not symbols:
            self.logger.warning("No symbols provided.")
            return None

        if not self.symbol_manager:
            self.logger.error("SymbolManager is not initialized.")
            return None

        if not self.stage_data_manager:
            self.logger.error("StageDataManager is not initialized.")
            return None

        if not self.portfolio_strategy_factory:
            self.logger.error("PortfolioStrategyFactory is not initialized.")
            return None

        self.logger.info(f"Retrieving portfolio strategy for symbols: {symbols}")
        return self.portfolio_strategy_factory.create_portfolio_strategy(
            symbols,
            self.stage_data_manager,
            self.evaluation_json_filename,
            self.viable_strategies_path,
            self.logger,
        )

    # def _get_optimized_params(
    #     self,
    #     symbols: list[str],
    #     strategy_name: str,
    # ) -> Optional[Dict[str, Any]]:
    #     """Retrieve optimized parameters for a given strategy and window ID."""
    #     try:
    #         self.logger.info(
    #             f"Retrieving optimized parameters for {strategy_name} during {self.train_window_id}"
    #         )
    #         train_opt_results = self._get_optimization_results(
    #             strategy_name=strategy_name,
    #             symbol=self._get_symbols_dir_name(symbols),
    #             start_date=self.train_start_date,
    #             end_date=self.train_end_date,
    #         )
    #         if not train_opt_results:
    #             self.logger.warning(
    #                 f"No optimization result for PORTFOLIO {strategy_name} {self.train_window_id}"
    #             )
    #             return None
    #         # Validate the optimization results structure
    #         if not self._validate_optimization_results(train_opt_results):
    #             self.logger.warning(
    #                 f"Validation failed for optimization results of {strategy_name} during {self.train_window_id}. Skipping."
    #             )
    #             return None

    #         best_params = train_opt_results[self.train_window_id]["optimization"][
    #             "best_params"
    #         ]
    #         valid_params = set(inspect.signature(strategy_class.__init__).parameters)
    #         filtered_params = {
    #             k: v
    #             for k, v in best_params.items()
    #             if k in valid_params and k != "self"
    #         }
    #         return filtered_params
    #     except Exception as e:
    #         self.logger.error(
    #             f"Error retrieving optimized parameters for {strategy_name} during {self.train_window_id}: {str(e)}"
    #         )
    #         return None

    # def _get_symbol_dir(
    #     self,
    #     symbol: str,
    # ) -> Path:
    #     """Get the path to the optimization result JSON file for a given strategy and symbol."""
    #     out_dir = self.stage_data_manager.get_directory_path(
    #         base_dir=self.optimization_root, symbol=symbol
    #     )
    #     out_dir.mkdir(parents=True, exist_ok=True)
    #     return out_dir
