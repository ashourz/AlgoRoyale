import pytest

from algo_royale.backtester.strategy.strategy_factory import StrategyFactory


class DummyStrategy:
    def __init__(self, **kwargs):
        self.params = kwargs


@pytest.fixture
def factory():
    # Use DummyStrategy for all strategy names for testing
    return StrategyFactory(
        available_strategies={
            "MovingAverageStrategy": DummyStrategy,
            "MomentumStrategy": DummyStrategy,
        }
    )


def test_get_merged_strategy_defs_defaults_and_symbol(factory):
    config = {
        "defaults": [{"name": "MovingAverageStrategy", "param_grid": {"a": [1]}}],
        "symbols": {"AAPL": [{"name": "MomentumStrategy", "param_grid": {"b": [2]}}]},
    }
    merged = factory._get_merged_strategy_defs("AAPL", config)
    assert len(merged) == 2
    assert merged[0]["name"] == "MovingAverageStrategy"
    assert merged[1]["name"] == "MomentumStrategy"


def test_create_backtest_strategies_param_grid(factory):
    config = {
        "defaults": [
            {
                "name": "MovingAverageStrategy",
                "param_grid": {"x": [1, 2], "y": [10, 20]},
            }
        ],
        "symbols": {},
    }
    all_symbols = ["AAPL"]
    result = factory.create_backtest_strategies(config, all_symbols)
    # Should create 4 strategies (2x2 grid)
    assert len(result["AAPL"]) == 4
    for strat in result["AAPL"]:
        assert isinstance(strat, DummyStrategy)
        assert set(strat.params.keys()) == {"x", "y"}


def test_create_backtest_strategies_params_singleton(factory):
    config = {
        "defaults": [{"name": "MovingAverageStrategy", "params": {"foo": 123}}],
        "symbols": {},
    }
    all_symbols = ["AAPL"]
    result = factory.create_backtest_strategies(config, all_symbols)
    assert len(result["AAPL"]) == 1
    assert result["AAPL"][0].params == {"foo": 123}


def test_create_backtest_strategies_symbol_specific(factory):
    config = {
        "defaults": [],
        "symbols": {
            "AAPL": [{"name": "MomentumStrategy", "param_grid": {"window": [5, 10]}}],
            "GOOG": [],
        },
    }
    all_symbols = ["AAPL", "GOOG"]
    result = factory.create_backtest_strategies(config, all_symbols)
    assert len(result["AAPL"]) == 2
    assert len(result["GOOG"]) == 0


def test_create_backtest_strategies_unknown_strategy(factory):
    config = {
        "defaults": [{"name": "NotARealStrategy", "param_grid": {}}],
        "symbols": {},
    }
    with pytest.raises(ValueError):
        factory.create_backtest_strategies(config, ["AAPL"])


def test_create_live_strategies(factory):
    config = {
        "defaults": [{"name": "MovingAverageStrategy", "params": {"foo": 1}}],
        "symbols": {"AAPL": [{"name": "MomentumStrategy", "params": {"bar": 2}}]},
    }
    all_symbols = ["AAPL", "GOOG"]
    result = factory.create_live_strategies(config, all_symbols)
    assert len(result["AAPL"]) == 2
    assert len(result["GOOG"]) == 1


def test_create_live_strategies_unknown_strategy(factory):
    config = {"defaults": [{"name": "NotARealStrategy", "params": {}}], "symbols": {}}
    with pytest.raises(ValueError):
        factory.create_live_strategies(config, ["AAPL"])


def test_create_live_strategies_from_file(tmp_path, factory):
    # Prepare a fake JSON file
    import json

    data = {
        "AAPL": [
            {"name": "MovingAverageStrategy", "params": {"foo": 1}},
            {"name": "MomentumStrategy", "params": {"bar": 2}},
        ]
    }
    file = tmp_path / "best_strategies.json"
    with open(file, "w") as f:
        json.dump(data, f)
    result = factory.create_live_strategies_from_file(str(file))
    assert len(result["AAPL"]) == 2
    assert isinstance(result["AAPL"][0], DummyStrategy)
    assert isinstance(result["AAPL"][1], DummyStrategy)


def test_create_live_strategies_from_file_unknown_strategy(tmp_path, factory):
    import json

    data = {"AAPL": [{"name": "NotARealStrategy", "params": {}}]}
    file = tmp_path / "bad_strategies.json"
    with open(file, "w") as f:
        json.dump(data, f)
    with pytest.raises(ValueError):
        factory.create_live_strategies_from_file(str(file))
