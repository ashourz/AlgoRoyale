from typing import Dict

import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enums.signal_type import SignalType
from algo_royale.backtester.strategy.signal.buffered_components.buffered_signal_strategy import (
    BufferedSignalStrategy,
)


class CombinedWeightedSignalStrategy:
    def __init__(
        self,
        buffered_strategies: Dict[BufferedSignalStrategy, float],
        buy_threshold: float = 0.5,
        sell_threshold: float = 0.5,
    ):
        """
        buffered_strategies: dict of {BufferedSignalStrategy instance: viability_score}
        Each BufferedSignalStrategy must have a .generate_signals(df) method.
        buy_threshold: minimum combined signal value to trigger a buy (default 0.5)
        sell_threshold: maximum combined signal value to trigger a sell (default -0.5)
        """
        self.buffered_strategies = buffered_strategies
        self.total_score = sum(buffered_strategies.values())
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def generate_signals(self, row: dict) -> pd.DataFrame:
        """
        Generate combined signals for each symbol, weighted by viability scores.
        Returns a DataFrame with combined signals.
        """
        combined_entry_signal = SignalType.HOLD.value
        combined_exit_signal = SignalType.HOLD.value
        # Entry signals
        total_entry_buy_weight = 0.0
        total_entry_hold_weight = 0.0

        # Exit signals
        total_exit_sell_weight = 0.0
        total_exit_hold_weight = 0.0

        for strategy, score in self.buffered_strategies.items():
            weight = score / self.total_score if self.total_score > 0 else 0
            signals = strategy.update(row)
            if signals is None:
                continue
            # Apply weight to each signal
            entry_signal = signals.get(
                SignalStrategyColumns.ENTRY_SIGNAL, SignalType.HOLD.value
            )
            if entry_signal == SignalType.BUY.value:
                total_entry_buy_weight += weight
            else:
                total_entry_hold_weight += weight
            self.logger.debug(
                f"Strategy {strategy.get_id()} signals: Entry: {entry_signal}, Weight: {weight}"
            )
            # Exit signal
            exit_signal = signals.get(
                SignalStrategyColumns.EXIT_SIGNAL, SignalType.HOLD.value
            )
            if exit_signal == SignalType.SELL.value:
                total_exit_sell_weight += weight
            else:
                total_exit_hold_weight += weight
            self.logger.debug(
                f"Strategy {strategy.get_id()} signals: Exit: {exit_signal}, Weight: {weight}"
            )

        # Determine combined entry signal
        if total_entry_buy_weight >= self.buy_threshold:
            combined_entry_signal = SignalType.BUY.value
        else:
            combined_entry_signal = SignalType.HOLD.value
        # Determine combined exit signal
        if total_exit_sell_weight >= self.sell_threshold:
            combined_exit_signal = SignalType.SELL.value
        else:
            combined_exit_signal = SignalType.HOLD.value
        self.logger.debug(
            f"Combined signals: Entry: BUY {total_entry_buy_weight}, HOLD {total_entry_hold_weight}, Exit: SELL {total_exit_sell_weight}, HOLD {total_exit_hold_weight}"
        )
        return {
            SignalStrategyColumns.ENTRY_SIGNAL: combined_entry_signal,
            SignalStrategyColumns.EXIT_SIGNAL: combined_exit_signal,
        }


# Usage:
# combined_strategy = CombinedWeightedSignalStrategy(all_buffered_strategies)
# signals = combined_strategy.generate_signals(df)
