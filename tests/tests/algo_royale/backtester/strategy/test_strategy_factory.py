import json
import os

import pytest

from algo_royale.strategy_factory.strategy_factory import StrategyFactory


class DummyConfig:
    def __init__(self, tmp_path):
        self._path = str(tmp_path / "strategy_map.json")

    def get(self, *args, **kwargs):
        return self._path


class DummyStrategy:
    def get_hash_id(self):
        return "dummy"

    def get_description(self):
        return "desc"

    def __class__(self):
        return type("DummyStrategy", (), {})()


@pytest.fixture
def config(tmp_path):
    return DummyConfig(tmp_path)


@pytest.fixture
def factory(config):
    return StrategyFactory(config=config)


def test_get_all_strategy_combinations_returns_list(factory, monkeypatch):
    # Patch all combinators to return dummy strategies
    dummy = DummyStrategy()
    for combinator in [
        "BollingerBandsStrategyCombinator",
        "ComboStrategyCombinator",
        "MACDTrailingStrategyCombinator",
        "MeanReversionStrategyCombinator",
        "MomentumStrategyCombinator",
        "MovingAverageCrossoverStrategyCombinator",
        "MovingAverageStrategyCombinator",
        "PullbackEntryStrategyCombinator",
        "RSIStrategyCombinator",
        "TimeOfDayBiasStrategyCombinator",
        "TrailingStopStrategyCombinator",
        "TrendScraperStrategyCombinator",
        "VolatilityBreakoutStrategyCombinator",
        "VolumeSurgeStrategyCombinator",
        "VWAPReversionStrategyCombinator",
        "WickReversalStrategyCombinator",
    ]:
        monkeypatch.setattr(
            f"algo_royale.strategy_factory.combinator.{combinator}",
            "get_all_combinations",
            staticmethod(lambda: [dummy]),
        )
    combos = factory.get_all_strategy_combinations()
    assert isinstance(combos, list)
    assert all(hasattr(s, "get_hash_id") for s in combos)
    assert all(hasattr(s, "get_description") for s in combos)


def test_save_strategy_map_creates_file(factory, tmp_path):
    # Use dummy strategies
    class Dummy:
        def __init__(self, i):
            self.i = i

        def get_hash_id(self):
            return f"id_{self.i}"

        def get_description(self):
            return f"desc_{self.i}"

        @property
        def __class__(self):
            class C:
                __name__ = "Dummy"

            return C

    strategies = [Dummy(i) for i in range(3)]
    factory.strategy_map_path = str(tmp_path / "out.json")
    factory._save_strategy_map(strategies)
    assert os.path.exists(factory.strategy_map_path)
    with open(factory.strategy_map_path) as f:
        data = json.load(f)
    assert "Dummy" in data
    assert all(f"id_{i}" in data["Dummy"] for i in range(3))
