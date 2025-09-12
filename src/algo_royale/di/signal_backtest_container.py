from dependency_injector import containers, providers

from algo_royale.backtester.evaluator.strategy.strategy_evaluation_coordinator import (
    StrategyEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.symbol.symbol_evaluation_coordinator import (
    SymbolEvaluationCoordinator,
)
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.stage_coordinator.optimization.strategy_optimization_stage_coordinator import (
    StrategyOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.testing.strategy_testing_stage_coordinator import (
    StrategyTestingStageCoordinator,
)
from algo_royale.backtester.walkforward.walk_forward_coordinator import (
    WalkForwardCoordinator,
)


class SignalBacktestContainer(containers.DeclarativeContainer):
    """Signal Backtest Container"""

    config = providers.Configuration()
    factory_container = providers.DependenciesContainer()
    logger_container = providers.DependenciesContainer()

    strategy_executor = providers.Singleton(
        StrategyBacktestExecutor,
        stage_data_manager=stage_data_manager,
        logger=logger_strategy_executor,
    )
    strategy_evaluator = providers.Singleton(
        SignalBacktestEvaluator,
        logger=logger_strategy_evaluator,
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
