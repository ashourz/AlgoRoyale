import pandas as pd
import pytest

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.strategy_factory.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class DummyCondition(StrategyCondition):
    def __init__(self, col, value=True):
        super().__init__(col=col, value=value)
        self.col = col
        self.value = value

    @property
    def required_columns(self):
        return {self.col}

    def apply(self, df):
        return pd.Series(self.value, index=df.index)


class DummyStatefulLogic(StatefulLogic):
    def __init__(self):
        super().__init__()

    def __call__(
        self,
        i,
        df,
        entry_signal=None,
        exit_signal=None,
        state=None,
        trend_mask=None,
        filter_mask=None,
        **kwargs,
    ):
        # Always set entry_signal to "buy" if filter_mask is True, else "hold"
        signal = "buy" if filter_mask.iloc[i] else "hold"
        return signal, exit_signal, state


def make_df():
    return pd.DataFrame(
        {
            "a": [1, 2, 3],
            "b": [4, 5, 6],
        }
    )


def test_required_columns():
    strat = Strategy(
        filter_conditions=[DummyCondition("a")],
        trend_conditions=[DummyCondition("b")],
        entry_conditions=[DummyCondition("a")],
        exit_conditions=[DummyCondition("b")],
    )
    cols = strat.required_columns
    assert set(cols) == {"a", "b"}


def test_apply_filters_and_trend():
    df = make_df()
    strat = Strategy(
        filter_conditions=[DummyCondition("a", value=True)],
        trend_conditions=[DummyCondition("b", value=True)],
        entry_conditions=[DummyCondition("a", value=True)],
        exit_conditions=[DummyCondition("b", value=False)],
    )
    signals = strat._apply_strategy(df)
    assert all(signals == "buy")


def test_apply_entry_exit():
    df = make_df()
    strat = Strategy(
        entry_conditions=[DummyCondition("a", value=True)],
        exit_conditions=[DummyCondition("b", value=True)],
    )
    entry = strat._apply_entry(df)
    exit_ = strat._apply_exit(df)
    assert all(entry)
    assert all(exit_)


def test_generate_signals_missing_column():
    df = pd.DataFrame({"a": [1, 2, 3]})
    strat = Strategy(entry_conditions=[DummyCondition("b")])
    with pytest.raises(ValueError):
        strat.generate_signals(df)


def test_generate_signals_with_stateful_logic():
    df = make_df()
    strat = Strategy(
        entry_conditions=[DummyCondition("a", value=True)],
        stateful_logic=DummyStatefulLogic(),
    )
    result = strat.generate_signals(df)
    assert all(result[StrategyColumns.ENTRY_SIGNAL] == "buy")


def test_get_description_and_hash_id():
    strat = Strategy(
        entry_conditions=[DummyCondition("a", value=True)],
        exit_conditions=[DummyCondition("b", value=False)],
    )
    desc = strat.get_description()
    hash_id = strat.get_hash_id()
    assert "Strategy" in desc
    assert isinstance(hash_id, str)
    assert len(hash_id) == 64
