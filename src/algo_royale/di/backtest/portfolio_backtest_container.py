from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from algo_royale.backtester.evaluator.backtest.portfolio_backtest_evaluator import (
    PortfolioBacktestEvaluator,
)
from algo_royale.backtester.evaluator.portfolio.portfolio_cross_strategy_summary import (
    PortfolioCrossStrategySummary,
)
from algo_royale.backtester.evaluator.portfolio.portfolio_cross_window_evaluator import (
    PortfolioCrossWindowEvaluator,
)
from algo_royale.backtester.evaluator.portfolio.portfolio_evaluation_coordinator import (
    PortfolioEvaluationCoordinator,
)
from algo_royale.backtester.executor.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)
from algo_royale.backtester.stage_coordinator.optimization.portfolio_optimization_stage_coordinator import (
    PortfolioOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.testing.portfolio_testing_stage_coordinator import (
    PortfolioTestingStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.portfolio_matrix_loader import (
    PortfolioMatrixLoader,
)
from algo_royale.backtester.walkforward.walk_forward_coordinator import (
    WalkForwardCoordinator,
)
from algo_royale.logging.logger_type import LoggerType
from algo_royale.utils.path_utils import get_project_root


# Refactored to a regular class
class PortfolioBacktestContainer:
    def __init__(
        self,
        config,
        data_prep_coordinator_container,
        stage_data_container,
        signal_backtest_container,
        factory_container,
        logger_container,
    ):
        self.config = config
        self.data_prep_coordinator_container = data_prep_coordinator_container
        self.stage_data_container = stage_data_container
        self.signal_backtest_container = signal_backtest_container
        self.factory_container = factory_container
        self.logger_container = logger_container

        self.data_dir = get_project_root() / self.config["data_dir"]["root"]

    @property
    def portfolio_executor(self) -> PortfolioBacktestExecutor:
        return PortfolioBacktestExecutor(
            initial_balance=float(
                self.config["backtester_portfolio"]["initial_portfolio_value"]
            ),
            transaction_cost=float(
                self.config["backtester_portfolio"]["transaction_costs"]
            ),
            min_lot=float(self.config["backtester_portfolio"]["minimum_lot_size"]),
            leverage=float(self.config["backtester_portfolio"]["leverage"]),
            slippage=float(self.config["backtester_portfolio"]["slippage"]),
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_BACKTEST_EXECUTOR
            ),
        )

    @property
    def portfolio_evaluator(self) -> PortfolioBacktestEvaluator:
        return PortfolioBacktestEvaluator(
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_BACKTEST_EVALUATOR
            ),
        )

    @property
    def portfolio_asset_matrix_preparer(self) -> AssetMatrixPreparer:
        return AssetMatrixPreparer(
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_ASSET_MATRIX_PREPARER
            ),
        )

    @property
    def portfolio_matrix_loader(self) -> PortfolioMatrixLoader:
        return PortfolioMatrixLoader(
            strategy_backtest_executor=self.signal_backtest_container.signal_strategy_executor,
            asset_matrix_preparer=self.portfolio_asset_matrix_preparer,
            stage_data_manager=self.stage_data_container.stage_data_manager,
            stage_data_loader=self.stage_data_container.stage_data_loader,
            strategy_factory=self.factory_container.signal_strategy_factory,
            data_dir=self.data_dir,
            optimization_root=self.config["backtester_signal_paths"][
                "signal_optimization_root_path"
            ],
            signal_summary_json_filename=self.config["backtester_signal_filenames"][
                "signal_summary_json_filename"
            ],
            symbol_signals_filename=self.config["backtester_signal_filenames"][
                "symbol_signals_filename"
            ],
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_MATRIX_LOADER
            ),
        )

    @property
    def portfolio_optimization_stage_coordinator(
        self,
    ) -> PortfolioOptimizationStageCoordinator:
        return PortfolioOptimizationStageCoordinator(
            data_loader=self.stage_data_container.symbol_strategy_data_loader,
            stage_data_manager=self.stage_data_container.stage_data_manager,
            executor=self.portfolio_executor,
            evaluator=self.portfolio_evaluator,
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_OPTIMIZATION
            ),
            strategy_combinator_factory=self.factory_container.portfolio_strategy_combinator_factory,
            optimization_root=self.config["backtester_portfolio_paths"][
                "portfolio_optimization_root_path"
            ],
            optimization_json_filename=self.config["backtester_portfolio_filenames"][
                "portfolio_optimization_json_filename"
            ],
            portfolio_matrix_loader=self.portfolio_matrix_loader,
            portfolio_strategy_optimizer_factory=self.factory_container.portfolio_strategy_optimizer_factory,
            optimization_n_trials=int(
                self.config["backtester_portfolio"]["optimization_n_trials"]
            ),
        )

    @property
    def portfolio_testing_stage_coordinator(self) -> PortfolioTestingStageCoordinator:
        return PortfolioTestingStageCoordinator(
            data_loader=self.stage_data_container.symbol_strategy_data_loader,
            stage_data_manager=self.stage_data_container.stage_data_manager,
            executor=self.portfolio_executor,
            evaluator=self.portfolio_evaluator,
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_TESTING
            ),
            strategy_logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_STRATEGY
            ),
            strategy_combinator_factory=self.factory_container.portfolio_strategy_combinator_factory,
            optimization_root=self.config["backtester_portfolio_paths"][
                "portfolio_optimization_root_path"
            ],
            optimization_json_filename=self.config["backtester_portfolio_filenames"][
                "portfolio_optimization_json_filename"
            ],
            portfolio_matrix_loader=self.portfolio_matrix_loader,
        )

    @property
    def portfolio_walk_forward_coordinator(self) -> WalkForwardCoordinator:
        return WalkForwardCoordinator(
            stage_data_manager=self.stage_data_container.stage_data_manager,
            stage_data_loader=self.stage_data_container.stage_data_loader,
            data_ingest_stage_coordinator=self.data_prep_coordinator_container.data_ingest_stage_coordinator,
            feature_engineering_stage_coordinator=self.data_prep_coordinator_container.feature_engineering_stage_coordinator,
            optimization_stage_coordinator=self.portfolio_optimization_stage_coordinator,
            testing_stage_coordinator=self.portfolio_testing_stage_coordinator,
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_WALK_FORWARD
            ),
            walk_forward_n_trials=int(
                self.config["backtester_portfolio"]["walk_forward_n_trials"]
            ),
            walk_forward_window_size=int(
                self.config["backtester_portfolio"]["walk_forward_window_size"]
            ),
        )

    @property
    def portfolio_cross_window_evaluator(self) -> PortfolioCrossWindowEvaluator:
        return PortfolioCrossWindowEvaluator(
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_CROSS_WINDOW_EVALUATOR
            ),
            window_json_filename=self.config["backtester_portfolio_filenames"][
                "portfolio_optimization_json_filename"
            ],
            output_filename=self.config["backtester_portfolio_filenames"][
                "portfolio_strategy_evaluation_json_filename"
            ],
        )

    @property
    def portfolio_cross_strategy_summary(self) -> PortfolioCrossStrategySummary:
        return PortfolioCrossStrategySummary(
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_CROSS_STRATEGY_SUMMARY
            ),
            evaluation_filename=self.config["backtester_portfolio_filenames"][
                "portfolio_strategy_evaluation_json_filename"
            ],
            output_filename=self.config["backtester_portfolio_filenames"][
                "portfolio_summary_json_filename"
            ],
        )

    @property
    def portfolio_evaluation_coordinator(self) -> PortfolioEvaluationCoordinator:
        return PortfolioEvaluationCoordinator(
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_EVALUATION
            ),
            cross_window_evaluator=self.portfolio_cross_window_evaluator,
            cross_strategy_summary=self.portfolio_cross_strategy_summary,
            optimization_root=self.config["backtester_portfolio_paths"][
                "portfolio_optimization_root_path"
            ],
            viability_threshold=float(
                self.config["backtester_portfolio"]["strategy_viability_threshold"]
            ),
        )
