from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.combo_entry import ComboEntryCondition
from algo_royale.strategies.conditions.combo_exit import ComboExitCondition


class ComboStrategy(Strategy):
    """
    Combo Strategy using RSI, MACD, and volume conditions for trading decisions.
    This strategy combines multiple indicators to determine entry and exit points:
    - RSI (Relative Strength Index) for overbought/oversold conditions.
    - MACD (Moving Average Convergence Divergence) for trend direction.
    - Volume to confirm the strength of the price movement.
    Parameters:
    - rsi_col: Column name for the RSI values.
    - macd_col: Column name for the MACD values.
    - volume_col: Column name for the trading volume.
    - vol_ma_col: Column name for the 20-day moving average of volume.
    - rsi_buy_thresh: Threshold for RSI to trigger a buy signal (default is 30).
    - rsi_sell_thresh: Threshold for RSI to trigger a sell signal (default is 70).
    - macd_buy_thresh: Threshold for MACD to trigger a buy signal (default is 0).
    - macd_sell_thresh: Threshold for MACD to trigger a sell signal (default is 0).

    Combo Strategy:
    - Buy when RSI < 30, MACD > 0, and volume > 20-day MA volume.
    - Sell when RSI > 70, MACD < 0, and volume < 20-day MA volume.
    - Hold otherwise.
    """

    def __init__(
        self,
        rsi_buy_thresh=30,
        rsi_sell_thresh=70,
        macd_buy_thresh=0,
        macd_sell_thresh=0,
        rsi_col=StrategyColumns.RSI,
        macd_col=StrategyColumns.MACD,
        volume_col=StrategyColumns.VOLUME,
        vol_ma_col=StrategyColumns.VOL_MA_20,
    ):
        entry_func = ComboEntryCondition(
            rsi_col=rsi_col,
            macd_col=macd_col,
            volume_col=volume_col,
            vol_ma_col=vol_ma_col,
            rsi_buy_thresh=rsi_buy_thresh,
            macd_buy_thresh=macd_buy_thresh,
        )
        exit_func = ComboExitCondition(
            rsi_col=rsi_col,
            macd_col=macd_col,
            volume_col=volume_col,
            vol_ma_col=vol_ma_col,
            rsi_sell_thresh=rsi_sell_thresh,
            macd_sell_thresh=macd_sell_thresh,
        )
        super().__init__(entry_conditions=[entry_func], exit_conditions=[exit_func])
