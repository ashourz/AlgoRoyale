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
from algo_royale.di.backtest.data_prep_coordinator_container import (
    DataPrepCoordinatorContainer,
)
from algo_royale.di.factory_container import FactoryContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.clock_service import ClockService


# Refactored to a regular class
class SignalBacktestContainer:
    def __init__(
        self,
        config,
        data_prep_coordinator_container: DataPrepCoordinatorContainer,
        stage_data_container: StageDataContainer,
        factory_container: FactoryContainer,
        clock_service: ClockService,
        logger_container: LoggerContainer,
    ):
        self.config = config
        self.data_prep_coordinator_container = data_prep_coordinator_container
        self.stage_data_container = stage_data_container
        self.factory_container = factory_container
        self.clock_service = clock_service
        self.logger_container = logger_container

    @property
    def signal_strategy_executor(self) -> StrategyBacktestExecutor:
        return StrategyBacktestExecutor(
            stage_data_manager=self.stage_data_container.stage_data_manager,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_EXECUTOR
            ),
        )

    @property
    def signal_strategy_evaluator(self) -> SignalBacktestEvaluator:
        return SignalBacktestEvaluator(
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_EVALUATOR
            ),
        )

    @property
    def strategy_optimization_stage_coordinator(
        self,
    ) -> SignalStrategyOptimizationStageCoordinator:
        return SignalStrategyOptimizationStageCoordinator(
            data_loader=self.stage_data_container.symbol_strategy_data_loader,
            stage_data_manager=self.stage_data_container.stage_data_manager,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_OPTIMIZATION
            ),
            strategy_combinator_factory=self.factory_container.signal_strategy_combinator_factory,
            strategy_executor=self.signal_strategy_executor,
            strategy_evaluator=self.signal_strategy_evaluator,
            optimization_root=self.config["backtester_signal_paths"][
                "signal_optimization_root_path"
            ],
            optimization_json_filename=self.config["backtester_signal_filenames"][
                "signal_optimization_json_filename"
            ],
            signal_strategy_optimizer_factory=self.factory_container.signal_strategy_optimizer_factory,
            optimization_n_trials=int(
                self.config["backtester_signal"]["optimization_n_trials"]
            ),
        )

    @property
    def strategy_testing_stage_coordinator(
        self,
    ) -> SignalStrategyTestingStageCoordinator:
        return SignalStrategyTestingStageCoordinator(
            data_loader=self.stage_data_container.symbol_strategy_data_loader,
            stage_data_manager=self.stage_data_container.stage_data_manager,
            strategy_executor=self.signal_strategy_executor,
            strategy_evaluator=self.signal_strategy_evaluator,
            strategy_factory=self.factory_container.signal_strategy_factory,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_TESTING
            ),
            strategy_combinator_factory=self.factory_container.signal_strategy_combinator_factory,
            optimization_root=self.config["backtester_signal_paths"][
                "signal_optimization_root_path"
            ],
            optimization_json_filename=self.config["backtester_signal_filenames"][
                "signal_optimization_json_filename"
            ],
        )

    @property
    def strategy_evaluation_coordinator(self) -> SignalStrategyEvaluationCoordinator:
        return SignalStrategyEvaluationCoordinator(
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_EVALUATION
            ),
            optimization_root=self.config["backtester_signal_paths"][
                "signal_optimization_root_path"
            ],
            evaluation_type=StrategyEvaluationType.BOTH,
            optimization_json_filename=self.config["backtester_signal_filenames"][
                "signal_optimization_json_filename"
            ],
            evaluation_json_filename=self.config["backtester_signal_filenames"][
                "signal_evaluation_json_filename"
            ],
        )

    @property
    def symbol_evaluation_coordinator(self) -> SymbolEvaluationCoordinator:
        return SymbolEvaluationCoordinator(
            optimization_root=self.config["backtester_signal_paths"][
                "signal_optimization_root_path"
            ],
            evaluation_json_filename=self.config["backtester_signal_filenames"][
                "signal_evaluation_json_filename"
            ],
            summary_json_filename=self.config["backtester_signal_filenames"][
                "signal_summary_json_filename"
            ],
            viability_threshold=float(
                self.config["backtester_signal"][
                    "signal_evaluation_viability_threshold"
                ]
            ),
            logger=self.logger_container.logger(
                logger_type=LoggerType.SYMBOL_EVALUATION
            ),
        )

    @property
    def signal_strategy_walk_forward_coordinator(self) -> WalkForwardCoordinator:
        return WalkForwardCoordinator(
            stage_data_manager=self.stage_data_container.stage_data_manager,
            stage_data_loader=self.stage_data_container.stage_data_loader,
            data_ingest_stage_coordinator=self.data_prep_coordinator_container.data_ingest_stage_coordinator,
            feature_engineering_stage_coordinator=self.data_prep_coordinator_container.feature_engineering_stage_coordinator,
            optimization_stage_coordinator=self.strategy_optimization_stage_coordinator,
            testing_stage_coordinator=self.strategy_testing_stage_coordinator,
            clock_service=self.clock_service,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SIGNAL_STRATEGY_WALK_FORWARD
            ),
            walk_forward_n_trials=int(
                self.config["backtester_signal"]["walk_forward_n_trials"]
            ),
            walk_forward_window_size=int(
                self.config["backtester_signal"]["walk_forward_window_size"]
            ),
        )
