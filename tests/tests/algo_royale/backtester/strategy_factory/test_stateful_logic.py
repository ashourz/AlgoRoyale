import pytest

from algo_royale.strategy_factory.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)


class DummyLogicNoParams(StatefulLogic):
    pass


class DummyLogicWithParams(StatefulLogic):
    @classmethod
    def available_param_grid(cls):
        return {
            "alpha": [0.1, 0.2],
            "beta": [1, 2],
        }


def test_call_raises_not_implemented():
    logic = DummyLogicNoParams()
    with pytest.raises(NotImplementedError):
        logic(0, None, None, None, None, None, None)


def test_available_param_grid_default():
    assert DummyLogicNoParams.available_param_grid() == {}


def test_all_possible_conditions_no_params():
    logics = DummyLogicNoParams.all_possible_conditions()
    assert len(logics) == 1
    assert isinstance(logics[0], DummyLogicNoParams)


def test_all_possible_conditions_with_params():
    logics = DummyLogicWithParams.all_possible_conditions()
    # 2 alphas x 2 betas = 4 combinations
    assert len(logics) == 4
    ids = [logic.get_id() for logic in logics]
    assert all(isinstance(i, str) for i in ids)
    expected = {
        "DummyLogicWithParams(alpha=0.1,beta=1)",
        "DummyLogicWithParams(alpha=0.1,beta=2)",
        "DummyLogicWithParams(alpha=0.2,beta=1)",
        "DummyLogicWithParams(alpha=0.2,beta=2)",
    }
    assert set(ids) == expected


def test_get_id_includes_class_and_params():
    logic = DummyLogicWithParams(alpha=0.5, beta=3)
    id_str = logic.get_id()
    assert "DummyLogicWithParams" in id_str
    assert "alpha=0.5" in id_str
    assert "beta=3" in id_str
