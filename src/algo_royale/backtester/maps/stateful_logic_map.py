from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)
from algo_royale.backtester.strategy.signal.stateful_logic.macd_trailing_stateful_logic import (
    MACDTrailingStatefulLogic,
)
from algo_royale.backtester.strategy.signal.stateful_logic.mean_reversion_stateful_logic import (
    MeanReversionStatefulLogic,
)
from algo_royale.backtester.strategy.signal.stateful_logic.trailing_stop_stateful_logic import (
    TrailingStopStatefulLogic,
)

STATEFUL_LOGIC_CLASS_MAP: dict[str, type[StatefulLogic]] = {
    "MACDTrailingStatefulLogic": MACDTrailingStatefulLogic,
    "MeanReversionStatefulLogic": MeanReversionStatefulLogic,
    "TrailingStopStatefulLogic": TrailingStopStatefulLogic,
}
