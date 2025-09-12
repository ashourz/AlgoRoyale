from dependency_injector import containers, providers

from algo_royale.backtester.evaluator.backtest.signal_backtest_evaluator import (
    SignalBacktestEvaluator,
)
from algo_royale.backtester.evaluator.strategy.signal_strategy_evaluation_coordinator import (
    SignalStrategyEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.strategy.strategy_evaluation_type import (
    StrategyEvaluationType,
)
from algo_royale.backtester.evaluator.symbol.symbol_evaluation_coordinator import (
    SymbolEvaluationCoordinator,
)
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.stage_coordinator.optimization.signal_strategy_optimization_stage_coordinator import (
    SignalStrategyOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.testing.signal_strategy_testing_stage_coordinator import (
    SignalStrategyTestingStageCoordinator,
)
from algo_royale.backtester.walkforward.walk_forward_coordinator import (
    WalkForwardCoordinator,
)
from algo_royale.logging.logger_type import LoggerType


class SignalBacktestContainer(containers.DeclarativeContainer):
    """Signal Backtest Container"""

    config = providers.Configuration()
    factory_container = providers.DependenciesContainer()
    stage_data_container = providers.DependenciesContainer()
    data_prep_coordinator_container = providers.DependenciesContainer()
    logger_container = providers.DependenciesContainer()

    signal_strategy_executor = providers.Singleton(
        StrategyBacktestExecutor,
        stage_data_manager=stage_data_container.stage_data_manager,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.SIGNAL_STRATEGY_EXECUTOR
        ),
    )
    signal_strategy_evaluator = providers.Singleton(
        SignalBacktestEvaluator,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.SIGNAL_STRATEGY_EVALUATOR
        ),
    )

    strategy_optimization_stage_coordinator = providers.Singleton(
        SignalStrategyOptimizationStageCoordinator,
        data_loader=stage_data_container.symbol_strategy_data_loader,
        stage_data_manager=stage_data_container.stage_data_manager,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.SIGNAL_STRATEGY_OPTIMIZATION
        ),
        strategy_combinator_factory=factory_container.signal_strategy_combinator_factory,
        strategy_executor=signal_strategy_executor,
        strategy_evaluator=signal_strategy_evaluator,
        optimization_root=config.backtester.signal.paths.signal_optimization_root_path,
        optimization_json_filename=config.backtester.signal.filenames.signal_optimization_json_filename,
        signal_strategy_optimizer_factory=factory_container.signal_strategy_optimizer_factory,
        optimization_n_trials=config.backtester.signal.optimization_n_trials,
    )

    strategy_testing_stage_coordinator = providers.Singleton(
        SignalStrategyTestingStageCoordinator,
        data_loader=stage_data_container.symbol_strategy_data_loader,
        stage_data_manager=stage_data_container.stage_data_manager,
        strategy_executor=signal_strategy_executor,
        strategy_evaluator=signal_strategy_evaluator,
        strategy_factory=factory_container.signal_strategy_factory,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.SIGNAL_STRATEGY_TESTING
        ),
        strategy_combinator_factory=factory_container.signal_strategy_combinator_factory,
        optimization_root=config.backtester.signal.paths.signal_optimization_root_path,
        optimization_json_filename=config.backtester.signal.filenames.signal_optimization_json_filename,
    )

    strategy_evaluation_coordinator = providers.Singleton(
        SignalStrategyEvaluationCoordinator,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.SIGNAL_STRATEGY_EVALUATION
        ),
        optimization_root=config.backtester.signal.paths.signal_optimization_root_path,
        evaluation_type=StrategyEvaluationType.BOTH,
        optimization_json_filename=config.backtester.signal.filenames.signal_optimization_json_filename,
        evaluation_json_filename=config.backtester.signal.filenames.signal_evaluation_json_filename,
    )

    symbol_evaluation_coordinator = providers.Singleton(
        SymbolEvaluationCoordinator,
        optimization_root=config.backtester.signal.paths.signal_optimization_root_path,
        evaluation_json_filename=config.backtester.signal.filenames.signal_evaluation_json_filename,
        summary_json_filename=config.backtester.signal.filenames.signal_summary_json_filename,
        viability_threshold=config.backtester.signal.signal_evaluation_viability_threshold,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.SYMBOL_EVALUATION
        ),
    )

    signal_strategy_walk_forward_coordinator = providers.Singleton(
        WalkForwardCoordinator,
        stage_data_manager=stage_data_container.stage_data_manager,
        stage_data_loader=stage_data_container.stage_data_loader,
        data_ingest_stage_coordinator=data_prep_coordinator_container.data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator=data_prep_coordinator_container.feature_engineering_stage_coordinator,
        optimization_stage_coordinator=strategy_optimization_stage_coordinator,
        testing_stage_coordinator=strategy_testing_stage_coordinator,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.SIGNAL_STRATEGY_WALK_FORWARD
        ),
    )
