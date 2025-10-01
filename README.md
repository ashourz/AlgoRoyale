


# AlgoRoyale

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

# 3. Backtest performance
results = backtest(strategy, historical_data)

# 4. Optimize strategy parameters
best_params = optimize(strategy, param_grid, historical_data)
```

---

## Getting Started

1. **Install dependencies** (uses Poetry):
   ```sh
   poetry install
   ```

2. **Configure environment**:
   - Copy `config.ini.example` to `config.ini` and fill in your API keys and settings.
   - Do **not** commit `config.ini` to GitHub.

3. **Run the orchestrator CLI**:
   ```sh
   poetry run python -m src.algo_royale.cli.trader_dev_integration
   ```

4. **Run the Flask API**:
   ```sh
   poetry run python src/app.py
   ```

5. **Run tests**:
   ```sh
   $env:PYTHONPATH=".\src;$env:PYTHONPATH"
   poetry run python -m unittest discover -s tests -p "test_*.py"
   ```

---

## Tech Stack

- **Python 3.10+**
- **Poetry** for dependency management
- **APScheduler** for job scheduling
- **Optuna** for optimization
- **Flask** for API
- **Pandas, Numpy** for data analysis
- **Alpaca API** for trading and market data

---

## License

MIT License
