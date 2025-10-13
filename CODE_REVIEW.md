# AlgoRoyale — Full Code Review

This document records a thorough code review of the AlgoRoyale repository (branch: main) and provides file-level findings, security observations, remediation recommendations, and a prioritized action plan suitable for inclusion in a portfolio or project handoff.

## Executive summary

AlgoRoyale demonstrates a mature architecture for an algorithmic trading platform. The codebase is modular, well-separated, DI-enabled, and includes both backtesting/optimization and live integrations with Alpaca. The major strengths are its architectural separation, integration tests/mocks, and pragmatic handling of streaming data.

Key risks found and remediations (high level):

- SQL injection / unsafe identifier interpolation: fixed in part, still needs audit of callers and tests. Use `psycopg2.sql.Identifier` & parameterized queries everywhere; add unit tests for validators.
- DB manager file corruption: earlier manual edits introduced duplicate code blocks — cleaned and replaced with canonical implementation.
- Stream client handshake and auth errors: multiple fixes applied (headers merging, correct connect param, avoid double-auth frames, use ws.ping()). Recommend adding unit tests/mocks around the stream client and a local integration harness.
- Missing tests around registries and DI wiring: add tests that verify DI containers supply correct factories and that `PortfolioStrategyRegistry` picks viable strategies.

## Review scope & methodology

I searched the repository for dynamic SQL patterns, cursor.execute calls, and f-strings embedding variables. I also inspected critical modules: Alpaca clients (market data + orders), strategy registry, market data streamer, database helpers, and DI containers.

Findings are grouped by priority and by file.

---

## High-priority issues (security, correctness)

1. Dynamic SQL interpolation (SQL injection)
   - Files with risky patterns found and fixed: `clients/db/user_manager.py`, `clients/db/database_manager.py`.
   - Action: audit all code paths that call `execute(query)` to ensure queries are parameterized; add unit tests verifying `is_valid_identifier()` rejects malicious input like `"; DROP TABLE users; --"`.

2. Corrupted file content in `database_manager.py`
   - Symptom: duplication/embedded class definitions introduced during edits led to syntax errors.
   - Action: file was fully replaced with a single canonical implementation that uses `psycopg2.sql` correctly. Run full CI checks and integration tests.

3. Alpaca WebSocket handshake/subscribe logic
   - Past issues: headers construction used a typing wrapper; wrong connect() kwarg; duplicate auth frames; empty subscribe lists; JSON ping frames causing 400 responses.
   - Action: fixes were applied: merged headers correctly, matched websockets.connect param, skipped duplicate auth frames, enforced non-empty subscription payloads, and used ws.ping(). Add unit/integration tests for the stream client using a mocked WebSocket server.

4. Market data ingestion shape mismatch
   - Problem: code assumed raw dicts and tried to subscript Pydantic model instances; KeyErrors occurred for missing ingest objects.
   - Action: `_onQuote` and `_onBar` were updated to accept either dicts or model instances and to lazily create ingest objects on first arrival.

---

## Medium-priority issues (robustness, maintainability)

1. Type annotations and consistent typing
   - Several modules lack full type annotations. Adding `mypy` and filling key interfaces will improve maintainability.

2. Concurrency model
   - Portfolio registry uses `threading.RLock` which is OK for mixed threading contexts, but if the application becomes fully asyncio-native, switch to `asyncio.Lock` for better semantics.

3. Tests coverage gaps
   - Add unit tests for:
     - `PortfolioStrategyRegistry` selection logic
     - DI containers wiring for factories
     - Alpaca stream client auth/subscribe/ping logic (with mocked WebSocket)
     - DB identifier validators and manager create/drop operations (mocked DB or test DB)

4. Config & env management
   - Centralize config parsing and document env vars. Consider `pydantic-settings` or `dynaconf` for typed config.

---

## File-level notes (selected important files)

- src/algo_royale/application/strategies/portfolio_strategy_registry.py
  - Purpose: choose the best viable strategy per symbol from symbol-level `summary_result.json`.
  - Status: recently updated to read symbol-level summary files, use `is_viable` flag, persist viable strategy map atomically, and guard in-memory map with RLock.
  - Recommendation: add tests for selection behavior and logging assertions.

- src/algo_royale/di/trading/registry_container.py
  - Purpose: DI wiring for strategy registries.
  - Recommendation: add an integration test that wires the real factory and asserts `PortfolioStrategyRegistry.get()` returns a strategy object for a known symbol with a viable summary.

- src/algo_royale/clients/alpaca/alpaca_base_client.py
  - Fixed bug: `.update()` return used as headers caused None to be returned; now returns a proper merged dict.

- src/algo_royale/clients/alpaca/alpaca_market_data/alpaca_stream_client.py
  - Several fixes applied to handshake and subscription logic. Add test harness.

- src/algo_royale/application/market_data/market_data_raw_streamer.py
  - Updated to accept both dict & parsed Pydantic models and lazily create ingest objects.

- src/algo_royale/clients/db/database_manager.py
  - Rewritten to remove duplicated/corrupted content; uses `psycopg2.sql.Identifier` now. Add unit tests that mock psycopg2 cursors to validate SQL executed.

- src/algo_royale/clients/db/user_manager.py
  - Rewritten to parameterize queries and use `sql.Identifier` for user identifiers.

- src/algo_royale/clients/db/dao/base_dao.py & src/algo_royale/clients/db/database.py
  - These provide a thin abstraction over `execute(query, params)` and are safe when callers provide parameters. Ensure callers don't craft raw SQL with untrusted inputs.

- Tests directory
  - Good coverage and mocks exist; expand integration tests focusing on stream -> ingestion -> strategy -> order flow.

---

## Security & hardening recommendations (concrete)

1. Enforce parameterized queries and identifiers everywhere.
2. Add unit tests for `is_valid_identifier` with edge cases and injection attempts.
3. Add CI job for static analysis (bandit) to catch obvious security issues.
4. Use secret management: `.env` for local dev, GitHub secrets for CI; document how to configure credentials securely.
5. Limit logging of sensitive values; create helper to redact secrets in logs.

---

## Suggested prioritized action plan

Immediate (1–2 days):

- SQL execute audit: completed. I inspected all `cur.execute(...)` call sites under `src/algo_royale/clients/db/` and verified they use safe patterns (parameterized queries, `psycopg2.sql.Identifier` for identifiers, or server-side `quote_ident` inside PL/pgSQL). Files reviewed:
  - `src/algo_royale/clients/db/user_manager.py` (uses `sql.Identifier` + parameterized password and validation via `is_valid_identifier`).
  - `src/algo_royale/clients/db/database_manager.py` (uses parameterized checks and `sql.Identifier`; `drop_all_tables` uses a server-side PL/pgSQL loop with `quote_ident`, which is safe on the server side).
  - `src/algo_royale/clients/db/migrations/migration_manager.py` (executes migration SQL files from the repo — expected behaviour; these files are trusted source-controlled SQL scripts).
  - `src/algo_royale/clients/db/database.py` (centralized `execute_query` helper that uses `cur.execute(query, params)` — callers should supply parameterized SQL and not format strings themselves).
  - `src/algo_royale/clients/db/dao/base_dao.py` and DAO implementations (load SQL from `sql/` files and call `cur.execute(query, params)` — this pattern is safe provided SQL files use `%s` placeholders and callers pass `params` tuples).

  Conclusion: I did not find remaining `cur.execute(...)` sites that build SQL using Python f-strings or simple concatenation. The patterns above are safe. That said, callers that read SQL files must be careful to pass parameters via the DB API rather than formatting them into the SQL files at runtime.

Follow-ups (recommended):
  - Add unit tests for `is_valid_identifier()` to assert behavior on malicious inputs (e.g. `"; DROP TABLE users; --"`) and edge cases (empty, >63 chars, invalid chars).
  - Add a CI check that scans the repository for suspicious patterns (simple grep for `cur.execute` occurrences that include `{` or `+` or `f"` in the adjacent lines) and fails the build if any are found. Optionally add a Bandit scan as a security lint step.
  - Add unit tests that mock a `psycopg2` cursor to assert that DDL functions call `cur.execute` with `sql.Identifier` objects where expected (this can be done with `unittest.mock` and asserting `.execute` call args contain `psycopg2.sql.Composed` / `Identifier`).
- Add unit tests for `is_valid_identifier` and basic DB manager operations (mock psycopg2).
- Add a smoke integration test that runs the stream client against a mocked websocket server to verify auth/subscribe flow.

Near-term (1–2 weeks):

- Add GitHub Actions CI: lint -> mypy -> pytest (unit) -> optional integration with dockerized Postgres.
- Add CONTRIBUTING.md and developer onboarding docs (how to run integration tests, required env vars).
- Add more type annotations and run mypy.

Medium (2–6 weeks):

- Add a minimal dashboard or CLI utilities for runtime strategy/symbol management.
- Provide Docker Compose for local dev (Postgres, mocked Alpaca, worker)
- Add runtime metrics and tracing (Prometheus / OpenTelemetry integration)

---

## Conclusion

AlgoRoyale is a robust starting point for a professional algorithmic trading platform. With a focused sprint to harden DB usage, add CI and tests, and create a reliable local integration environment, it will be excellent for a professional portfolio and production deployments.
