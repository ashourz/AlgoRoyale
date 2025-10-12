import json
import os

import pytest

from algo_royale.application.strategies.portfolio_strategy_registry import (
    PortfolioStrategyRegistry,
)
from tests.mocks.mock_loggable import MockLoggable


class MockSymbolService:
    pass


class MockStageDataManager:
    def get_directory_path(self, base_dir, symbol):
        path = os.path.join(base_dir, symbol)
        os.makedirs(path, exist_ok=True)
        return type(
            "PathLike",
            (),
            {
                "mkdir": lambda self, **kwargs: None,
                "exists": lambda self: True,
                "stat": lambda self: type("stat", (), {"st_size": 1})(),
                "__truediv__": lambda self, other: self,
                "name": symbol,
                "iterdir": lambda self: [],
            },
        )()


class MockPortfolioStrategyFactory:
    def build_buffered_strategy(self, strategy_class, params):
        return f"BufferedStrategy({strategy_class}, {params})"


@pytest.fixture
def registry(tmp_path):
    viable_strategies_path = tmp_path / "viable_strategies.json"
    viable_strategies_path.write_text(json.dumps({}))
    return PortfolioStrategyRegistry(
        symbol_service=MockSymbolService(),
        stage_data_manager=MockStageDataManager(),
        strategy_summary_json_filename="eval.json",
        viable_strategies_path=str(viable_strategies_path),
        portfolio_strategy_factory=MockPortfolioStrategyFactory(),
        optimization_root_path=str(tmp_path / "optimization"),
        logger=MockLoggable(),
    )


class TestPortfolioStrategyRegistry:
    def test_get_buffered_portfolio_strategy_none(self, registry):
        result = registry.get_buffered_portfolio_strategy(["AAPL"])
        assert result is None

    def test_get_buffered_portfolio_strategy_exception(self, registry, monkeypatch):
        monkeypatch.setattr(
            registry,
            "_get_symbols_dir_name",
            lambda symbols: (_ for _ in ()).throw(Exception("fail")),
        )
        result = registry.get_buffered_portfolio_strategy(["AAPL"])
        assert result is None

    def test_load_existing_viable_strategy_params_json_error(self, registry, tmp_path):
        # Write invalid JSON
        path = tmp_path / "bad.json"
        path.write_text("{bad json}")
        registry.viable_strategies_path = path
        registry._load_existing_viable_strategy_params()
        assert isinstance(registry.portfolio_strategy_map, dict)

    def test_sync_viable_strategy_params_exception(self, registry, monkeypatch):
        monkeypatch.setattr(registry, "portfolio_strategy_map", {"AAPL": object()})
        registry.viable_strategies_path = "/invalid/path/viable_strategies.json"
        registry._sync_viable_strategy_params()  # Should not raise

    def test_update_portfolio_strategy_map_empty(self, registry):
        result = registry._update_portfolio_strategy_map(["AAPL"])
        assert result is None or isinstance(result, dict)

    def test_get_buffered_portfolio_strategy_unknown_class(self, registry, monkeypatch):
        monkeypatch.setattr(
            registry,
            "portfolio_strategy_map",
            {"AAPL": {"name": "Unknown", "params": {}}},
        )
        result = registry.get_buffered_portfolio_strategy(["AAPL"])
        assert result is None

    def test_get_symbols_dir_name(self, registry):
        assert registry._get_symbols_dir_name(["GOOG", "AAPL"]) == "AAPL_GOOG"
        assert registry._get_symbols_dir_name([]) == "empty"
