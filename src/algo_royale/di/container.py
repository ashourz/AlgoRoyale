from functools import partial

from dependency_injector import containers, providers

from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from algo_royale.backtester.data_preparer.stage_data_preparer import StageDataPreparer
from algo_royale.backtester.evaluator.backtest.portfolio_backtest_evaluator import (
    PortfolioBacktestEvaluator,
)
from algo_royale.backtester.evaluator.backtest.signal_backtest_evaluator import (
    SignalBacktestEvaluator,
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
from algo_royale.backtester.evaluator.strategy.strategy_evaluation_coordinator import (
    StrategyEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.strategy.strategy_evaluation_type import (
    StrategyEvaluationType,
)
from algo_royale.backtester.evaluator.symbol.symbol_evaluation_coordinator import (
    SymbolEvaluationCoordinator,
)
from algo_royale.backtester.executor.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.feature_engineering.backtest_feature_engineer import (
    BacktestFeatureEngineer,
)
from algo_royale.backtester.feature_engineering.feature_engineering import (
    feature_engineering,
)
from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer_factory import (
    PortfolioStrategyOptimizerFactoryImpl,
)
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    SignalStrategyOptimizerFactoryImpl,
)
from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.data_staging.feature_engineering_stage_coordinator import (
    FeatureEngineeringStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.optimization.portfolio_optimization_stage_coordinator import (
    PortfolioOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.optimization.strategy_optimization_stage_coordinator import (
    StrategyOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.testing.portfolio_testing_stage_coordinator import (
    PortfolioTestingStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.testing.strategy_testing_stage_coordinator import (
    StrategyTestingStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.portfolio_matrix_loader import (
    PortfolioMatrixLoader,
)
from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.writer.stage_data_writer import StageDataWriter
from algo_royale.backtester.stage_data.writer.symbol_strategy_data_writer import (
    SymbolStrategyDataWriter,
)
from algo_royale.backtester.strategy.signal.manager.symbol_strategy_manager import (
    SymbolStrategyManager,
)
from algo_royale.backtester.strategy_factory.portfolio.portfolio_strategy_combinator_factory import (
    PortfolioStrategyCombinatorFactory,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_combinator_factory import (
    SignalStrategyCombinatorFactory,
)
from algo_royale.backtester.strategy_factory.signal.strategy_factory import (
    StrategyFactory,
)
from algo_royale.backtester.walkforward.walk_forward_coordinator import (
    WalkForwardCoordinator,
)
from algo_royale.repo.watchlist_repo import WatchlistRepo
from algo_royale.utils.path_utils import get_data_dir
from algo_royale.visualization.dashboard import BacktestDashboard


class DIContainer(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    alpaca_quote_service = providers.Singleton(
        QuoteAdapter, alpaca_stock_client=alpaca_stock_client
    )

    data_dir = get_data_dir()
    ## Backtester
    stage_data_manager = providers.Singleton(
        StageDataManager, data_dir=data_dir, logger=logger_stage_data_manager
    )

    stage_data_preparer = providers.Singleton(
        StageDataPreparer,
        stage_data_manager=stage_data_manager,
        logger=logger_stage_data_preparer,
    )

    watchlist_path_string = providers.Object(
        config().get("backtester.paths", "watchlist_path")
    )

    watchlist_repo = providers.Singleton(
        WatchlistRepo, watchlist_path=watchlist_path_string
    )

    stage_data_loader = providers.Singleton(
        StageDataLoader,
        logger=logger_stage_data_loader,
        stage_data_manager=stage_data_manager,
        watchlist_repo=watchlist_repo,
    )

    stage_data_writer = providers.Singleton(
        StageDataWriter,
        logger=logger_stage_data_writer,
        stage_data_manager=stage_data_manager,
    )

    feature_engineering_func = providers.Object(
        partial(feature_engineering, logger=logger_backtest_feature_engineering())
    )

    feature_engineer = providers.Singleton(
        BacktestFeatureEngineer,
        feature_engineering_func=feature_engineering_func,
        logger=logger_backtest_feature_engineering,
    )

    backtest_dashboard = providers.Singleton(
        BacktestDashboard,
        config=config,
    )

    symbol_strategy_data_loader = providers.Singleton(
        SymbolStrategyDataLoader,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        logger=logger_symbol_strategy_data_loader,
    )

    symbol_strategy_data_writer = providers.Singleton(
        SymbolStrategyDataWriter,
        stage_data_manager=stage_data_manager,
        data_writer=stage_data_writer,
        logger=logger_symbol_strategy_data_writer,
    )

    data_ingest_stage_coordinator = providers.Singleton(
        DataIngestStageCoordinator,
        data_loader=stage_data_loader,
        data_writer=symbol_strategy_data_writer,
        data_manager=stage_data_manager,
        logger=logger_backtest_data_ingest,
        quote_service=alpaca_quote_service,
        watchlist_repo=watchlist_repo,
    )

    feature_engineering_stage_coordinator = providers.Singleton(
        FeatureEngineeringStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        data_writer=symbol_strategy_data_writer,
        data_manager=stage_data_manager,
        logger=logger_backtest_feature_engineering,
        feature_engineer=feature_engineer,
    )

    # Strategy backtest executor
    strategy_executor = providers.Singleton(
        StrategyBacktestExecutor,
        stage_data_manager=stage_data_manager,
        logger=logger_strategy_executor,
    )
    strategy_evaluator = providers.Singleton(
        SignalBacktestEvaluator,
        logger=logger_strategy_evaluator,
    )

    signal_strategy_combinator_factory = providers.Singleton(
        SignalStrategyCombinatorFactory,
        combinator_list_path=providers.Object(
            config().get("backtester.paths", "signal_strategy_combinators")
        ),
        logger=logger_signal_strategy_combinator_factory,
    )

    strategy_factory = providers.Singleton(
        StrategyFactory,
        logger=logger_strategy_factory,
        strategy_logger=logger_signal_strategy,
    )

    signal_strategy_optimizer_factory = providers.Singleton(
        SignalStrategyOptimizerFactoryImpl,
        logger=logger_signal_strategy_optimizer,
        strategy_logger=logger_signal_strategy,
    )

    strategy_optimization_stage_coordinator = providers.Singleton(
        StrategyOptimizationStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        stage_data_manager=stage_data_manager,
        logger=logger_backtest_signal_optimization,
        strategy_combinator_factory=signal_strategy_combinator_factory,
        strategy_executor=strategy_executor,
        strategy_evaluator=strategy_evaluator,
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_optimization_json_filename"
            )
        ),
        signal_strategy_optimizer_factory=signal_strategy_optimizer_factory,
        optimization_n_trials=providers.Object(
            config().get_int("backtester.signal", "optimization_n_trials", 1)
        ),
    )

    strategy_testing_stage_coordinator = providers.Singleton(
        StrategyTestingStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        stage_data_manager=stage_data_manager,
        strategy_executor=strategy_executor,
        strategy_evaluator=strategy_evaluator,
        strategy_factory=strategy_factory,
        logger=logger_backtest_signal_testing,
        strategy_combinator_factory=signal_strategy_combinator_factory,
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_optimization_json_filename"
            )
        ),
    )

    strategy_walk_forward_coordinator = providers.Singleton(
        WalkForwardCoordinator,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        data_ingest_stage_coordinator=data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator=feature_engineering_stage_coordinator,
        optimization_stage_coordinator=strategy_optimization_stage_coordinator,
        testing_stage_coordinator=strategy_testing_stage_coordinator,
        logger=logger_strategy_walk_forward,
    )

    symbol_strategy_manager = providers.Singleton(
        SymbolStrategyManager,
        data_dir=get_data_dir(),
        stage_data_manager=stage_data_manager,
        symbol_strategy_evaluation_filename=providers.Object(
            config().get("backtester.signal.filenames", "signal_summary_json_filename")
        ),
        logger=logger_symbol_strategy_manager,
    )

    portfolio_executor = providers.Singleton(
        PortfolioBacktestExecutor,
        initial_balance=providers.Object(
            config().get_float(
                "backtester.portfolio", "initial_portfolio_value", 1_000_000.0
            )
        ),
        transaction_cost=providers.Object(
            config().get_float("backtester.portfolio", "transaction_costs", 0.0)
        ),
        min_lot=providers.Object(
            config().get_int("backtester.portfolio", "minimum_lot_size", 1)
        ),
        leverage=providers.Object(
            config().get_float("backtester.portfolio", "leverage", 1.0)
        ),
        slippage=providers.Object(
            config().get_float("backtester.portfolio", "slippage", 0.0)
        ),
        logger=logger_portfolio_executor,
    )

    portfolio_evaluator = providers.Singleton(
        PortfolioBacktestEvaluator,
        logger=logger_portfolio_evaluator,
    )

    portfolio_strategy_combinator_factory = providers.Singleton(
        PortfolioStrategyCombinatorFactory,
        combinator_list_path=providers.Object(
            config().get("backtester.paths", "portfolio_strategy_combinators")
        ),
        logger=logger_portfolio_strategy_combinator_factory,
        strategy_logger=logger_portfolio_strategy,
    )

    portfolio_asset_matrix_preparer = providers.Singleton(
        AssetMatrixPreparer,
        logger=logger_portfolio_asset_matrix_preparer,
    )

    portfolio_matrix_loader = providers.Singleton(
        PortfolioMatrixLoader,
        strategy_backtest_executor=strategy_executor,
        asset_matrix_preparer=portfolio_asset_matrix_preparer,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        strategy_factory=strategy_factory,
        data_dir=get_data_dir(),
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        signal_summary_json_filename=providers.Object(
            config().get("backtester.signal.filenames", "signal_summary_json_filename")
        ),
        symbol_signals_filename=providers.Object(
            config().get("backtester.signal.filenames", "symbol_signals_filename")
        ),
        logger=logger_portfolio_matrix_loader,
    )

    portfolio_strategy_optimizer_factory = providers.Singleton(
        PortfolioStrategyOptimizerFactoryImpl,
        logger=logger_portfolio_strategy_optimizer,
        strategy_logger=logger_portfolio_strategy,
    )

    portfolio_optimization_stage_coordinator = providers.Singleton(
        PortfolioOptimizationStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        stage_data_manager=stage_data_manager,
        executor=portfolio_executor,
        evaluator=portfolio_evaluator,
        logger=logger_backtest_portfolio_optimization,
        strategy_combinator_factory=portfolio_strategy_combinator_factory,
        optimization_root=providers.Object(
            config().get(
                "backtester.portfolio.paths", "portfolio_optimization_root_path"
            ),
        ),
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames", "portfolio_optimization_json_filename"
            )
        ),
        portfolio_matrix_loader=portfolio_matrix_loader,
        portfolio_strategy_optimizer_factory=portfolio_strategy_optimizer_factory,
        optimization_n_trials=providers.Object(
            config().get_int("backtester.portfolio", "optimization_n_trials", 1)
        ),
    )

    portfolio_testing_stage_coordinator = providers.Singleton(
        PortfolioTestingStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        stage_data_manager=stage_data_manager,
        executor=portfolio_executor,
        evaluator=portfolio_evaluator,
        logger=logger_backtest_portfolio_testing,
        strategy_logger=logger_portfolio_strategy,
        strategy_combinator_factory=portfolio_strategy_combinator_factory,
        optimization_root=providers.Object(
            config().get(
                "backtester.portfolio.paths", "portfolio_optimization_root_path"
            ),
        ),
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames", "portfolio_optimization_json_filename"
            )
        ),
        portfolio_matrix_loader=portfolio_matrix_loader,
    )

    portfolio_walk_forward_coordinator = providers.Singleton(
        WalkForwardCoordinator,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        data_ingest_stage_coordinator=data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator=feature_engineering_stage_coordinator,
        optimization_stage_coordinator=portfolio_optimization_stage_coordinator,
        testing_stage_coordinator=portfolio_testing_stage_coordinator,
        logger=logger_portfolio_walk_forward,
    )

    strategy_evaluation_coordinator = providers.Singleton(
        StrategyEvaluationCoordinator,
        logger=logger_strategy_evaluation,
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        evaluation_type=StrategyEvaluationType.BOTH,
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_optimization_json_filename"
            )
        ),
        evaluation_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_evaluation_json_filename"
            )
        ),
    )

    symbol_evaluation_coordinator = providers.Singleton(
        SymbolEvaluationCoordinator,
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        evaluation_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_evaluation_json_filename"
            )
        ),
        summary_json_filename=providers.Object(
            config().get("backtester.signal.filenames", "signal_summary_json_filename")
        ),
        viability_threshold=providers.Object(
            config().get_float(
                "backtester.signal", "signal_evaluation_viability_threshold", 0.5
            )
        ),
        logger=logger_symbol_evaluation,
    )

    portfolio_cross_window_evaluator = providers.Singleton(
        PortfolioCrossWindowEvaluator,
        logger=logger_portfolio_evaluation,
        window_json_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames", "portfolio_optimization_json_filename"
            )
        ),
        output_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames",
                "portfolio_strategy_evaluation_json_filename",
            )
        ),
    )
    portfolio_cross_strategy_summary = providers.Singleton(
        PortfolioCrossStrategySummary,
        logger=logger_portfolio_evaluation,
        evaluation_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames",
                "portfolio_strategy_evaluation_json_filename",
            )
        ),
        output_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames",
                "portfolio_summary_json_filename",
            )
        ),
    )
    # Portfolio evaluation coordinator
    portfolio_evaluation_coordinator = providers.Singleton(
        PortfolioEvaluationCoordinator,
        logger=logger_portfolio_evaluation,
        cross_window_evaluator=portfolio_cross_window_evaluator,
        cross_strategy_summary=portfolio_cross_strategy_summary,
        optimization_root=providers.Object(
            config().get(
                "backtester.portfolio.paths", "portfolio_optimization_root_path"
            )
        ),
        viability_threshold=providers.Object(
            config().get_float(
                "backtester.portfolio", "strategy_viability_threshold", 0.5
            )
        ),
    )
    pipeline_coordinator = providers.Singleton(
        PipelineCoordinator,
        strategy_walk_forward_coordinator=strategy_walk_forward_coordinator,
        portfolio_walk_forward_coordinator=portfolio_walk_forward_coordinator,
        strategy_evaluation_coordinator=strategy_evaluation_coordinator,
        symbol_evaluation_coordinator=symbol_evaluation_coordinator,
        portfolio_evaluation_coordinator=portfolio_evaluation_coordinator,
        logger=logger_backtest_pipeline,
    )


di_container = DIContainer()
