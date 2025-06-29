import pytest

from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class DummyConditionNoParams(StrategyCondition):
    pass


class DummyConditionWithParams(StrategyCondition):
    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "threshold": [1, 2],
            "window": [10, 20],
        }


class DummyLogger:
    def info(self, msg, *args):
        print(msg % args)

    def debug(self, msg, *args):
        print


def test_apply_raises_not_implemented():
    cond = DummyConditionNoParams()
    with pytest.raises(NotImplementedError):
        cond.apply(None)


def test_available_param_grid_default():
    assert DummyConditionNoParams.available_param_grid() == {}


def test_all_possible_conditions_no_params():
    conds = DummyConditionNoParams.all_possible_conditions(logger=DummyLogger())
    assert len(conds) == 1
    assert isinstance(conds[0], DummyConditionNoParams)


def test_all_possible_conditions_with_params():
    conds = DummyConditionWithParams.all_possible_conditions(logger=DummyLogger())
    # 2 thresholds x 2 windows = 4 combinations
    assert len(conds) == 4
    ids = [c.get_id() for c in conds]
    assert all(isinstance(i, str) for i in ids)
    # Ensure all parameter combinations are present
    expected = {
        "DummyConditionWithParams(threshold=1,window=10)",
        "DummyConditionWithParams(threshold=1,window=20)",
        "DummyConditionWithParams(threshold=2,window=10)",
        "DummyConditionWithParams(threshold=2,window=20)",
    }
    assert set(ids) == expected


def test_get_id_includes_class_and_params():
    cond = DummyConditionWithParams(threshold=5, window=15)
    id_str = cond.get_id()
    assert "DummyConditionWithParams" in id_str
    assert "threshold=5" in id_str
    assert "window=15" in id_str
