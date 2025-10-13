

# AlgoRoyale

A modular, production-grade algorithmic trading orchestration platform focused on reproducible research (backtesting & optimization), safe paper/live execution, and clear separation between research and runtime.

This README has been updated to reflect the current codebase (no assumptions). It documents the actual backtest pipeline, the trading runtime, configuration points, and the exact CLI entry points provided in `src/algo_royale/cli/`.

---

## Quick highlights

- Backtesting and optimization are implemented as a configurable pipeline (walk-forward, optimization, testing, and evaluation) driven by `PipelineCoordinator` and `WalkForwardCoordinator`.
- The trading runtime is driven by `TradeOrchestrator` which schedules market sessions and starts `MarketSessionService` components that manage live/paper trading tasks.
- Dependency injection is used via `ApplicationContainer` (found in `src/algo_royale/di/`) to wire repositories, adapters, factories, and services per environment.
- Database migrations and environment setup are invoked from the CLI via the repository container (call site: `repo_container.db_container.setup_environment()`).
- CLI entry points exist per named environment (dev_integration, prod_paper, prod_live) for both backtesting and trading; each CLI uses a file-lock (`SingleInstanceLock`) to avoid concurrent runs.

---

## Backtest pipeline (authoritative)

Core coordinator classes and flow (these classes exist in `src/algo_royale/backtester/`):

- `PipelineCoordinator` (backtester/pipeline): orchestrates the high-level pipeline. It runs:
  - strategy walk-forward coordinator (signal strategy optimization)
  - signal strategy evaluation
  - symbol evaluation
  - portfolio walk-forward coordinator (portfolio optimization)
  - portfolio evaluation

- `WalkForwardCoordinator` (backtester/walkforward): runs walk-forward windows and invokes stage coordinators for each window.

- Optimization stage coordinators (examples in `backtester/stage_coordinator/optimization`):
  - `SignalStrategyOptimizationStageCoordinator`
  - `PortfolioOptimizationStageCoordinator`

Artifacts and filenames

- Stage coordinators write JSON artifacts under the configured optimization root via the project's `StageDataManager` and stage-data loaders. Filenames and roots are configurable in the project's config. Typical JSON artifacts contain keys used by the runtime registries and evaluators, for example:
  - `is_viable` (boolean)
  - `most_common_best_params` or `best_params` (parameter dict)
  - `strategy` (strategy class name)
  - `meta` (run metadata such as runtime, trials, symbols)

See `backtester/stage_coordinator/optimization/signal_strategy_optimization_stage_coordinator.py` and `backtester/stage_data/loader/*` for the exact writer logic and filename config keys (the pipeline uses `optimization_json_filename`, `evaluation_json_filename`, and similar configuration keys).

Running backtests (CLI)

The repository provides CLI entry points that create the DI `ApplicationContainer`, call database setup/migrations, and run the coordinator under a single-instance lock. Example modules:

- `src.algo_royale.cli.backtest_dev_integration` — backtest pipeline in DEV_INTEGRATION env
- `src.algo_royale.cli.backtest_prod_paper` — backtest pipeline in PROD_PAPER env
- `src.algo_royale.cli.backtest_prod_live` — backtest pipeline in PROD_LIVE env

Example (PowerShell):

```powershell
# Activate your venv and run the backtest pipeline in the dev_integration environment
poetry run python -m src.algo_royale.cli.backtest_dev_integration
```

Notes:

- There is no top-level `optimize_symbol` or `run_backtest` module in this repository; per-symbol and portfolio optimization are performed by the backtest pipeline and its stage coordinators. Filenames and the optimization root are configurable; inspect `src/algo_royale/di/backtest/` and `src/algo_royale/config/` for exact keys.

---

## Trading runtime (authoritative)

The runtime trading workflow is implemented in `src/algo_royale/services/` and wired by the trading DI container. Key pieces:

- `TradeOrchestrator` (`src/algo_royale/services/trade_orchestrator.py`)
  - Schedules market session jobs using `ClockService` and starts/stops the `MarketSessionService` at pre-market, open, and close events.

- `MarketSessionService`
  - Manages lifecycle for the trading day: starts premarket tasks, market tasks, and stops/cleans up after close. (See `src/algo_royale/services/market_session_service.py`.)

- Market data ingestion
  - Market data is normalized by Alpaca adapters under `src/algo_royale/clients/alpaca/` and streamed through `MarketDataEnrichedStreamer`/`MarketDataRawStreamer` (in `src/algo_royale/application/market_data/`). The streamer normalizes websocket messages into internal models (quotes/bars) and can accept either raw dicts or parsed model instances.

- Signal generation
  - `SignalGenerator` subscribes to enriched market-data events and uses a `SignalStrategyRegistry` to instantiate combined/weighted signal strategies for symbols. Signals are emitted via an async pub/sub helper.

- Portfolio & order generation
  - `PortfolioStrategyRegistry` selects per-symbol or portfolio strategies based on optimization artifacts produced by the backtest pipeline (it expects the optimization artifacts under the stage data directories and uses configured filenames).
  - `OrderGenerator` consumes signals and portfolio state and deterministically produces order instructions for the orders adapter. In the codebase it returns an empty list when no strategy is available for a symbol.

- Order dispatch and adapters
  - `OrderEventService` and adapter implementations translate order instructions to Alpaca order API calls (see `src/algo_royale/clients/alpaca/` and adapter containers in `src/algo_royale/di/adapter`).

Runtime CLI entry points

- `src.algo_royale.cli.trader_dev_integration`
- `src.algo_royale.cli.trader_prod_paper`
- `src.algo_royale.cli.trader_prod_live`

These CLI modules build an `ApplicationContainer(environment=ApplicationEnv.X)`, call `repo_container.db_container.setup_environment()`, then start the `trade_orchestrator` under a `SingleInstanceLock` (lock file present next to the module).

---

## Configuration & DI

- The application uses a set of DI containers under `src/algo_royale/di/` to assemble the runtime and backtest pipelines. The top-level container is `ApplicationContainer` which wires:
  - repo containers (DB, migration helpers)
  - adapter containers (Alpaca adapters, market data adapters)
  - backtest pipeline containers (data prep, signal & portfolio backtests)
  - trading container (order generator, registries, orchestrator)

- Environment-specific logging types and configuration live under `src/algo_royale/logging/` and `src/algo_royale/config/`.

---

## Persistence and DB

- Database migrations and environment setup are handled by the repo container and invoked from CLI modules (see `repo_container.db_container.setup_environment()` in the CLI implementations).
- Database helper modules in `src/algo_royale/clients/db/` use parameterized queries and (where necessary) `psycopg2.sql.Identifier` for safe identifier interpolation. See the code review notes in `CODE_REVIEW.md` for details and recommended tests.

---

## Running tests and development

- Install dependencies (this project uses Poetry):

```powershell
poetry install
```

- Run unit tests:

```powershell
poetry run pytest -q
```

- Lint/format with your preferred tools (`black`, `isort`, `flake8`, `mypy`).

---

## License

MIT License

