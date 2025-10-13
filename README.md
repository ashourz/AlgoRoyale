

# AlgoRoyale

> **A modular, production-grade algorithmic trading orchestration platform for equities and derivatives, supporting research, live trading, and portfolio optimization.**

**AlgoRoyale** is a modular, production-grade algorithmic trading orchestration platform for equities. It is designed for robust, automated trading, and portfolio backtest optimization, with a focus on extensibility, observability, and clean architecture.

---

## Features

- **Automated Trading Orchestration**: Schedules and manages market session jobs (pre-market, open, close) using APScheduler and a custom orchestrator.
- **Modular Service Architecture**: Clean separation of concerns with dependency injection (via `dependency_injector`), supporting easy extension and testing.
- **Portfolio Management**: Integrates with Alpaca API for real-time portfolio data, order execution, and historical analysis.
- **Backtesting & Optimization**: Includes a flexible backtesting engine and portfolio strategy optimizer (Optuna-based) for research and parameter tuning.
- **CLI & API**: Run as a CLI daemon for live trading, or as a Flask API for research and integration.
- **Robust Logging**: Centralized, taggable logging system with support for multiple loggers and granular log types.
- **Data Ingestion & Feature Engineering**: Modular pipelines for ingesting and transforming market data.
- **Single-Instance Locking**: Prevents accidental multiple orchestrator instances.
- **Extensive Test Suite**: Pytest-based, with async and mock support.

---

## Architecture

- **src/algo_royale/**: Core trading logic, orchestrators, services, and dependency injection containers.
- **clients/alpaca/**: Alpaca API integration for trading and market data.
- **feature_engineering/**: Feature extraction and transformation modules.
- **optimization/**: Portfolio optimization and signal generation.
- **scripts/**: Utility scripts for setup, data management, and automation.
- **tests/**: Comprehensive unit and integration tests.

---


## Usage & Configuration


Currently, all configuration—including symbol lists, signal and portfolio strategies, and their parameters—is managed via config files (such as `config.ini`). There is no external interface for updating these settings at runtime. In the future, as visualization and dashboard features are developed, API routes or UI controls will be provided to update strategies, symbols, and parameters dynamically.

This project supports **separate logging and application environments** for development (unit/integration) and production (live and paper trading). Each environment has its own CLI entry point, exposed as a separate Poetry command, ensuring isolated configuration, logging, and runtime behavior for each use case.

> **Note:** This project is a work in progress. Many features, including external configuration and visualization, are planned but not yet implemented.

---

## Example Usage

```python
# 1. Select a strategy
strategy = MovingAverageStrategy(window=20)

# 2. Generate signals
signals = strategy.generate_signals(historical_data)
# AlgoRoyale

> A production-minded algorithmic trading orchestration platform for equities — research, optimization, and live execution.

AlgoRoyale is designed to demonstrate professional, production-oriented architecture for algorithmic trading. It brings together real-time market-data ingestion, robust backtesting, portfolio optimization, and live order execution with clear separation of concerns, testability, and observability.

---

Badges
- Add CI / Coverage / PyPI badges here when available.

## Table of contents
- Features
- Quick start
- Architecture & diagrams
- Configuration & environments
- Development & testing
- Security & best practices
- Code review summary (link)
- Roadmap
- Contributing
- License

## Features

- Modular service architecture with dependency injection (dependency_injector)
- Real-time market-data ingestion and normalization (Alpaca adapters)
- Order execution and market session orchestration (pre-market, open, close)
- Portfolio strategy framework and buffered strategy adapter
- Backtesting and parameter optimization (Optuna)
- Centralized, taggable logging with per-environment config
- Data pipelines for feature engineering and research
- Postgres-based persistence and migration utilities
- CLI entry points for multiple environments (dev, dev_integration, production)

## Quick start

1. Install dependencies (Poetry):

```powershell
poetry install
```

2. Configure environment (example):

- Copy the example config for the environment you want to run (e.g. `env_config_dev_integration.ini.example`) and fill in API keys and DB credentials.
- Keep secrets out of source control (use a `.env` locally and CI secrets in GitHub Actions).

3. Run the development/integration CLI:

```powershell
poetry run python -m src.algo_royale.cli.trader_dev_integration
```

4. Run tests:

```powershell
# $env:PYTHONPATH=".\src;$env:PYTHONPATH"
poetry run pytest -q
```

## Architecture & diagrams

The codebase is organized into clear modules:

- `src/algo_royale/application` — orchestrators, services, order generation, strategy registries
- `src/algo_royale/clients` — external integrations (Alpaca, Postgres helpers)
- `src/algo_royale/backtester` — backtesting and strategy implementations
- `src/algo_royale/feature_engineering` — feature extraction and transforms
- `src/algo_royale/optimization` — Optuna-based optimization and results
- `tests` — unit and integration tests and mocks

High level data flow (Mermaid):

```mermaid
flowchart LR
  subgraph STREAM
    A[Alpaca WebSocket] -->|messages| B[Alpaca Stream Client]
  end
  B --> C[MarketDataRawStreamer]
  C --> D[StreamDataIngestObject(s)]
  D --> E[Feature Engineering Pipelines]
  E --> F[Backtester / Signal Generators]
  F --> G[Portfolio Strategy Registry]
  G --> H[BufferedPortfolioStrategy]
  H --> I[OrderGenerator]
  I --> J[Alpaca Orders Client]
  J --> K[Broker]
  subgraph DB
    L[Postgres: state, users, migrations]
  end
  F --> L
  G --> L
  I --> L
```

Notes:

- The `PortfolioStrategyRegistry` reads persisted optimization summaries and selects viable strategies per symbol.
- The `BufferedPortfolioStrategy` wraps compact strategies and exposes a stable interface for `OrderGenerator` to produce orders.

## Configuration & environments

- Multiple CLI entry points and environment configs are provided for `dev`, `dev_integration`, and `production`.
- Logging is environment-specific with tags and environment loggers (dev_integration logs are configured for tighter diagnostics).
- Secrets: store API keys and DB credentials outside the repo. Use `.env` or a secret manager in CI.

## Development & testing

- Use `poetry` to manage dependencies and virtualenv.
- Run linters (black/flake8/isort) and type checks (mypy) before committing.
- Tests: `pytest` for unit and integration tests. Some integration tests require a running Postgres or use mocks.

CI suggestions

- Add GitHub Actions to run: lint -> mypy -> pytest (unit) -> optional integration job with Dockerized Postgres.

## Security & best practices

- Database safety: always use parameterized queries and `psycopg2.sql.Identifier` for identifiers. Identifier validators are included.
- Don't log secrets. Redact or avoid printing credentials in logs.
- Migration SQL files should be trusted and code-reviewed before applying in production.

## Code review summary

See `CODE_REVIEW.md` for a detailed, file-level code review, findings, and remediation plan. This includes security notes, tests to add, and next steps to harden the codebase for production.

## Roadmap

- Add GitHub Actions CI + coverage and badges
- Add CONTRIBUTING.md and developer onboarding steps
- Add a minimal dashboard/UI to manage symbols & strategies
- Harden integration tests and provide docker-compose for local dev

## Contributing

- Open an issue or PR. Run linters/tests locally before submitting.

## License

MIT License
