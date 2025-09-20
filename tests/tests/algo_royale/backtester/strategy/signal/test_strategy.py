import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)
from tests.mocks.mock_loggable import MockLoggable


class DummyCondition(StrategyCondition):
    def __init__(self, col, value=True):
        super().__init__(col=col, value=value)
        self.col = col
        self.value = value

    @property
    def required_columns(self):
        return [self.col]

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
    strat = BaseSignalStrategy(
        filter_conditions=[DummyCondition("a")],
        trend_conditions=[DummyCondition("b")],
        entry_conditions=[DummyCondition("a")],
        exit_conditions=[DummyCondition("b")],
        logger=MockLoggable(),
    )
    cols = strat.required_columns
    assert set(cols) == {"a", "b"}


def test_apply_filters_and_trend():
    df = make_df()
    strat = BaseSignalStrategy(
        filter_conditions=[DummyCondition("a", value=True)],
        trend_conditions=[DummyCondition("b", value=True)],
        entry_conditions=[DummyCondition("a", value=True)],
        exit_conditions=[DummyCondition("b", value=False)],
        logger=MockLoggable(),
    )
    signals = strat._apply_strategy(df)
    assert all(signals == "buy")


def test_apply_entry_exit():
    df = make_df()
    strat = BaseSignalStrategy(
        entry_conditions=[DummyCondition("a", value=True)],
        exit_conditions=[DummyCondition("b", value=True)],
        logger=MockLoggable(),
    )
    entry = strat._apply_entry(df)
    exit_ = strat._apply_exit(df)
    assert all(entry)
    assert all(exit_)


def test_generate_signals_missing_column():
    df = pd.DataFrame({"a": [1, 2, 3]})
    strat = BaseSignalStrategy(
        entry_conditions=[DummyCondition("b")], logger=MockLoggable()
    )
    result = strat.generate_signals(df)
    assert all(result[SignalStrategyColumns.ENTRY_SIGNAL] == "hold")
    assert all(result[SignalStrategyColumns.EXIT_SIGNAL] == "hold")


def test_generate_signals_with_stateful_logic():
    df = make_df()
    strat = BaseSignalStrategy(
        entry_conditions=[DummyCondition("a", value=True)],
        stateful_logic=DummyStatefulLogic(),
        logger=MockLoggable(),
    )
    result = strat.generate_signals(df)
    assert all(result[SignalStrategyColumns.ENTRY_SIGNAL] == "buy")


def test_get_description_and_hash_id():
    strat = BaseSignalStrategy(
        entry_conditions=[DummyCondition("a", value=True)],
        exit_conditions=[DummyCondition("b", value=False)],
        logger=MockLoggable(),
    )
    desc = strat.get_description()
    hash_id = strat.get_hash_id()
    assert "Strategy" in desc
    assert isinstance(hash_id, str)
    assert len(hash_id) == 64
