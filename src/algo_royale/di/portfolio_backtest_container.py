from dependency_injector import containers, providers


class PortfolioBacktestContainer(containers.DeclarativeContainer):
    """Portfolio Backtest Container"""

    config = providers.Configuration()
    factory_container = providers.DependenciesContainer()
    logger_container = providers.DependenciesContainer()

    stage_data_manager = providers.Dependency()
    portfolio_matrix_loader = providers.Dependency()
    symbol_strategy_data_loader = providers.Dependency()

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
