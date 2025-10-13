import json
import os

import pytest

from algo_royale.application.strategies.signal_strategy_registry import (
    SignalStrategyRegistry,
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


class MockSignalStrategyFactory:
    def build_buffered_strategy(self, strategy_class, params):
        return f"BufferedSignalStrategy({strategy_class}, {params})"


class MockCombinedWeightedSignalStrategy:
    def __init__(self, buffered_strategies, buy_threshold, sell_threshold):
        self.buffered_strategies = buffered_strategies
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold


@pytest.fixture
def registry(tmp_path):
    viable_strategies_path = tmp_path / "viable_strategies.json"
    viable_strategies_path.write_text(json.dumps({}))
    return SignalStrategyRegistry(
        symbol_service=MockSymbolService(),
        stage_data_manager=MockStageDataManager(),
        evaluation_json_filename="eval.json",
        viable_strategies_path=str(viable_strategies_path),
        signal_strategy_factory=MockSignalStrategyFactory(),
        logger=MockLoggable(),
        optimization_root_path=str(tmp_path / "optimization"),
        combined_buy_threshold=0.5,
        combined_sell_threshold=0.5,
    )


class TestSignalStrategyRegistry:
    def test_get_combined_weighted_signal_strategy_none(self, registry):
        result = registry.get_combined_weighted_signal_strategy("AAPL")
        assert result is None

    def test_get_combined_weighted_signal_strategy_exception(
        self, registry, monkeypatch
    ):
        monkeypatch.setattr(
            registry,
            "_get_symbol_dir",
            lambda symbol: (_ for _ in ()).throw(Exception("fail")),
        )
        result = registry.get_combined_weighted_signal_strategy("AAPL")
        assert result is None

    def test_load_existing_viable_strategy_params_json_error(self, registry, tmp_path):
        # Write invalid JSON
        path = tmp_path / "bad.json"
        path.write_text("{bad json}")
        registry.viable_strategies_path = path
        registry._load_existing_viable_strategy_params()
        assert isinstance(registry.symbol_strategy_map, dict)

    def test_sync_viable_strategy_params_exception(self, registry, monkeypatch):
        monkeypatch.setattr(registry, "symbol_strategy_map", {"AAPL": object()})
        registry.viable_strategies_path = "/invalid/path/viable_strategies.json"
        registry._sync_viable_strategy_params()  # Should not raise

    def test_update_symbol_strategy_map_empty(self, registry):
        result = registry._update_symbol_strategy_map("AAPL")
        assert result is None or isinstance(result, dict)

    def test_get_combined_weighted_signal_strategy_unknown_class(
        self, registry, monkeypatch
    ):
        monkeypatch.setattr(
            registry,
            "symbol_strategy_map",
            {"AAPL": {"Unknown": {"viability_score": 1, "params": {}}}},
        )
        result = registry.get_combined_weighted_signal_strategy("AAPL")
        assert result is None
