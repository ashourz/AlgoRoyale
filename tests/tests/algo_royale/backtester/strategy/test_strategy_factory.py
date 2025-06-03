import json

import pytest

from algo_royale.strategy_factory.strategy_factory import StrategyFactory


class DummyStrategy:
    def __init__(self, **kwargs):
        self.params = kwargs


@pytest.fixture
def strategy_map():
    return {
        "MovingAverageStrategy": DummyStrategy,
        "MomentumStrategy": DummyStrategy,
    }


@pytest.fixture
def factory(strategy_map):
    return StrategyFactory(strategy_map=strategy_map)


def write_json(tmp_path, data) -> str:
    file = tmp_path / "strategies.json"
    with open(file, "w") as f:
        json.dump(data, f)
    return str(file)


def test_create_strategies_param_grid(tmp_path, factory):
    config = {
        "defaults": [
            {
                "name": "MovingAverageStrategy",
                "param_grid": {"x": [1, 2], "y": [10, 20]},
            }
        ],
        "symbols": {"AAPL": []},
    }
    json_path = write_json(tmp_path, config)
    result = factory.create_strategies(json_path)
    assert len(result["AAPL"]) == 4
    for strat in result["AAPL"]:
        assert isinstance(strat, DummyStrategy)
        assert set(strat.params.keys()) == {"x", "y"}


def test_create_strategies_params_singleton(tmp_path, factory):
    config = {
        "defaults": [{"name": "MovingAverageStrategy", "params": {"foo": 123}}],
        "symbols": {"AAPL": []},
    }
    json_path = write_json(tmp_path, config)
    result = factory.create_strategies(json_path)
    assert len(result["AAPL"]) == 1
    assert result["AAPL"][0].params == {"foo": 123}


def test_create_strategies_symbol_specific(tmp_path, factory):
    config = {
        "defaults": [],
        "symbols": {
            "AAPL": [{"name": "MomentumStrategy", "param_grid": {"window": [5, 10]}}],
            "GOOG": [],
        },
    }
    json_path = write_json(tmp_path, config)
    result = factory.create_strategies(json_path)
    assert len(result["AAPL"]) == 2
    assert len(result["GOOG"]) == 0


def test_create_strategies_unknown_strategy(tmp_path, factory):
    config = {
        "defaults": [{"name": "NotARealStrategy", "param_grid": {}}],
        "symbols": {"AAPL": []},
    }
    json_path = write_json(tmp_path, config)
    with pytest.raises(ValueError):
        factory.create_strategies(json_path)


def test_create_strategies_defaults_and_symbol(tmp_path, factory):
    config = {
        "defaults": [{"name": "MovingAverageStrategy", "param_grid": {"a": [1]}}],
        "symbols": {"AAPL": [{"name": "MomentumStrategy", "param_grid": {"b": [2]}}]},
    }
    json_path = write_json(tmp_path, config)
    result = factory.create_strategies(json_path)
    assert len(result["AAPL"]) == 2
    names = [type(s).__name__ for s in result["AAPL"]]
    assert names.count("DummyStrategy") == 2
