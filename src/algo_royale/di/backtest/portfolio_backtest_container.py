from dependency_injector import containers, providers

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


class PortfolioBacktestContainer(containers.DeclarativeContainer):
    """Portfolio Backtest Container"""

    config = providers.Configuration()
    factory_container = providers.DependenciesContainer()
    stage_data_container = providers.DependenciesContainer()
    signal_backtest_container = providers.DependenciesContainer()
    data_prep_coordinator_container = providers.DependenciesContainer()
    logger_container = providers.DependenciesContainer()

    def get_data_dir(config) -> str:
        return get_project_root() / config.data.dir.root()

    data_dir = providers.Callable(get_data_dir, config=config)

    portfolio_executor = providers.Singleton(
        PortfolioBacktestExecutor,
        initial_balance=config.backtester.portfolio.initial_portfolio_value,
        transaction_cost=config.backtester.portfolio.transaction_costs,
        min_lot=config.backtester.portfolio.minimum_lot_size,
        leverage=config.backtester.portfolio.leverage,
        slippage=config.backtester.portfolio.slippage,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_BACKTEST_EXECUTOR
        ),
    )

    portfolio_evaluator = providers.Singleton(
        PortfolioBacktestEvaluator,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_BACKTEST_EVALUATOR
        ),
    )

    portfolio_asset_matrix_preparer = providers.Singleton(
        AssetMatrixPreparer,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_ASSET_MATRIX_PREPARER
        ),
    )

    portfolio_matrix_loader = providers.Singleton(
        PortfolioMatrixLoader,
        strategy_backtest_executor=signal_backtest_container.signal_strategy_executor,
        asset_matrix_preparer=portfolio_asset_matrix_preparer,
        stage_data_manager=stage_data_container.stage_data_manager,
        stage_data_loader=stage_data_container.stage_data_loader,
        strategy_factory=factory_container.signal_strategy_factory,
        data_dir=data_dir,
        optimization_root=config.backtester.signal.paths.signal_optimization_root_path,
        signal_summary_json_filename=config.backtester.signal.filenames.signal_summary_json_filename,
        symbol_signals_filename=config.backtester.signal.filenames.symbol_signals_filename,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_MATRIX_LOADER
        ),
    )

    portfolio_optimization_stage_coordinator = providers.Singleton(
        PortfolioOptimizationStageCoordinator,
        data_loader=stage_data_container.symbol_strategy_data_loader,
        stage_data_manager=stage_data_container.stage_data_manager,
        executor=portfolio_executor,
        evaluator=portfolio_evaluator,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_OPTIMIZATION
        ),
        strategy_combinator_factory=factory_container.portfolio_strategy_combinator_factory,
        optimization_root=config.backtester.portfolio.paths.portfolio_optimization_root_path,
        optimization_json_filename=config.backtester.portfolio.filenames.portfolio_optimization_json_filename,
        portfolio_matrix_loader=portfolio_matrix_loader,
        portfolio_strategy_optimizer_factory=factory_container.portfolio_strategy_optimizer_factory,
        optimization_n_trials=config.backtester.portfolio.optimization_n_trials,
    )

    portfolio_testing_stage_coordinator = providers.Singleton(
        PortfolioTestingStageCoordinator,
        data_loader=stage_data_container.symbol_strategy_data_loader,
        stage_data_manager=stage_data_container.stage_data_manager,
        executor=portfolio_executor,
        evaluator=portfolio_evaluator,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_TESTING
        ),
        strategy_logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_STRATEGY
        ),
        strategy_combinator_factory=factory_container.portfolio_strategy_combinator_factory,
        optimization_root=config.backtester.portfolio.paths.portfolio_optimization_root_path,
        optimization_json_filename=config.backtester.portfolio.filenames.portfolio_optimization_json_filename,
        portfolio_matrix_loader=portfolio_matrix_loader,
    )

    portfolio_walk_forward_coordinator = providers.Singleton(
        WalkForwardCoordinator,
        stage_data_manager=stage_data_container.stage_data_manager,
        stage_data_loader=stage_data_container.stage_data_loader,
        data_ingest_stage_coordinator=data_prep_coordinator_container.data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator=data_prep_coordinator_container.feature_engineering_stage_coordinator,
        optimization_stage_coordinator=portfolio_optimization_stage_coordinator,
        testing_stage_coordinator=portfolio_testing_stage_coordinator,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_WALK_FORWARD
        ),
    )

    portfolio_cross_window_evaluator = providers.Singleton(
        PortfolioCrossWindowEvaluator,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_CROSS_WINDOW_EVALUATOR
        ),
        window_json_filename=config.backtester.portfolio.filenames.portfolio_optimization_json_filename,
        output_filename=config.backtester.portfolio.filenames.portfolio_strategy_evaluation_json_filename,
    )

    portfolio_cross_strategy_summary = providers.Singleton(
        PortfolioCrossStrategySummary,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_CROSS_STRATEGY_SUMMARY
        ),
        evaluation_filename=config.backtester.portfolio.filenames.portfolio_strategy_evaluation_json_filename,
        output_filename=config.backtester.portfolio.filenames.portfolio_summary_json_filename,
    )
    # Portfolio evaluation coordinator
    portfolio_evaluation_coordinator = providers.Singleton(
        PortfolioEvaluationCoordinator,
        logger=logger_container.logger.provider(
            logger_type=LoggerType.PORTFOLIO_EVALUATION
        ),
        cross_window_evaluator=portfolio_cross_window_evaluator,
        cross_strategy_summary=portfolio_cross_strategy_summary,
        optimization_root=config.backtester.portfolio.paths.portfolio_optimization_root_path,
        viability_threshold=config.backtester.portfolio.strategy_viability_threshold,
    )
