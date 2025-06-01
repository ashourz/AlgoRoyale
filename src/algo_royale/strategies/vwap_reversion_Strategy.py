from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.vwap_reversion_entry import (
    VWAPReversionEntryCondition,
)
from algo_royale.strategies.conditions.vwap_reversion_exit import (
    VWAPReversionExitCondition,
)


class VWAPReversionStrategy(Strategy):
    """
    VWAP Reversion Strategy:
    - Buy when volume-weighted price is significantly below the VWAP.
    - Sell when volume-weighted price is significantly above the VWAP.
    - Hold otherwise.
    """

    def __init__(
        self,
        deviation_threshold: float = 0.01,
        vwap_col: str = "vwap_20",
        vwp_col: str = "volume_weighted_price",
    ):
        self.deviation_threshold = deviation_threshold
        self.vwap_col = vwap_col
        self.vwp_col = vwp_col

        self.entry_conditions = [
            VWAPReversionEntryCondition(
                deviation_threshold=deviation_threshold,
                vwap_col=vwap_col,
                vwp_col=vwp_col,
            )
        ]
        self.exit_conditions = [
            VWAPReversionExitCondition(
                deviation_threshold=deviation_threshold,
                vwap_col=vwap_col,
                vwp_col=vwp_col,
            )
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
