import numpy as np
import pandas as pd

from algo_royale.backtester.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)
from algo_royale.logging.loggable import Loggable


class FeatureEngineer:
    def __init__(self, logger: Loggable):
        self.logger = logger

    def compute_max_lookback(self) -> int:
        try:
            return FeatureEngineeringColumns.get_max_lookback_from_columns()
        except Exception as e:
            self.logger.error(f"Error computing max lookback: {e}")
            return 1

    def _compute_pct_return(self, df: pd.DataFrame) -> float:
        if len(df) < 2:
            self.logger.warning("Not enough data to compute percent return.")
            return float("nan")
        try:
            prev = df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-2]
            curr = df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-1]
            return (curr - prev) / prev if prev != 0 else float("nan")
        except Exception as e:
            self.logger.error(f"Error computing single percent return: {e}")
            return float("nan")

    def _compute_log_return(self, df: pd.DataFrame) -> float:
        if len(df) < 2:
            self.logger.warning("Not enough data to compute log return.")
            return float("nan")
        try:
            prev = df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-2]
            curr = df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-1]
            return (
                np.log(curr) - np.log(prev) if prev > 0 and curr > 0 else float("nan")
            )
        except Exception as e:
            self.logger.error(f"Error computing single log return: {e}")
            return float("nan")

    def _compute_sma(self, df: pd.DataFrame, window: int) -> float:
        if len(df) < window:
            self.logger.warning(f"Not enough data to compute SMA for window {window}.")
            return float("nan")
        try:
            return df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-window:].mean()
        except Exception as e:
            self.logger.error(f"Error computing single SMA for window {window}: {e}")
            return float("nan")

    def _compute_ema(self, df: pd.DataFrame, window: int) -> float:
        if len(df) < window:
            self.logger.warning(f"Not enough data to compute EMA for window {window}.")
            return float("nan")
        try:
            ema_series = (
                df[FeatureEngineeringColumns.CLOSE_PRICE]
                .ewm(span=window, adjust=False)
                .mean()
            )
            return ema_series.iloc[-1]
        except Exception as e:
            self.logger.error(f"Error computing single EMA for window {window}: {e}")
            return float("nan")

    def _compute_macd(self, df: pd.DataFrame) -> float:
        try:
            ema_12 = (
                df[FeatureEngineeringColumns.CLOSE_PRICE]
                .ewm(span=12, adjust=False)
                .mean()
            )
            ema_26 = (
                df[FeatureEngineeringColumns.CLOSE_PRICE]
                .ewm(span=26, adjust=False)
                .mean()
            )
            return (
                (ema_12.iloc[-1] - ema_26.iloc[-1]) if len(df) >= 26 else float("nan")
            )
        except Exception as e:
            self.logger.error(f"Error computing single MACD: {e}")
            return float("nan")

    def _compute_macd_signal(self, df: pd.DataFrame) -> float:
        try:
            if FeatureEngineeringColumns.MACD not in df.columns or len(df) < 9:
                self.logger.warning(
                    "MACD column missing or not enough data for MACD signal."
                )
                return float("nan")
            macd_signal = (
                df[FeatureEngineeringColumns.MACD].ewm(span=9, adjust=False).mean()
            )
            return macd_signal.iloc[-1]
        except Exception as e:
            self.logger.error(f"Error computing single MACD signal: {e}")
            return float("nan")

    def _compute_rsi(self, df: pd.DataFrame, window=14) -> float:
        try:
            if len(df) < window:
                self.logger.warning(
                    f"Not enough data to compute RSI for window {window}."
                )
                return float("nan")
            delta = df[FeatureEngineeringColumns.CLOSE_PRICE].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.ewm(
                alpha=1 / window, min_periods=window, adjust=False
            ).mean()
            avg_loss = loss.ewm(
                alpha=1 / window, min_periods=window, adjust=False
            ).mean()
            rs = avg_gain / avg_loss
            rsi_series = 100 - (100 / (1 + rs))
            return rsi_series.iloc[-1].replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(f"Error calculating single RSI: {e}")
            return float("nan")

    def _compute_volatility(self, df: pd.DataFrame, window: int) -> float:
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute volatility for window {window}."
            )
            return float("nan")
        try:
            vol_series = (
                df[FeatureEngineeringColumns.PCT_RETURN].rolling(window=window).std()
            )
            return vol_series.iloc[-1]
        except Exception as e:
            self.logger.error(
                f"Error computing single volatility for window {window}: {e}"
            )
            return float("nan")

    def _compute_hist_volatility(self, df: pd.DataFrame, window: int) -> float:
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute historical volatility for window {window}."
            )
            return float("nan")
        try:
            hist_vol_series = df[FeatureEngineeringColumns.PCT_RETURN].rolling(
                window=window
            ).std() * np.sqrt(252)
            return hist_vol_series.iloc[-1]
        except Exception as e:
            self.logger.error(
                f"Error computing single historical volatility for window {window}: {e}"
            )
            return float("nan")

    def _compute_atr(self, df: pd.DataFrame, window=14) -> float:
        try:
            if len(df) < window:
                self.logger.warning(
                    f"Not enough data to compute ATR for window {window}."
                )
                return float("nan")
            high = df[FeatureEngineeringColumns.HIGH_PRICE]
            low = df[FeatureEngineeringColumns.LOW_PRICE]
            close = df[FeatureEngineeringColumns.CLOSE_PRICE]
            tr = pd.concat(
                [high - low, (high - close.shift()).abs(), (low - close.shift()).abs()],
                axis=1,
            ).max(axis=1)
            atr_series = tr.rolling(window=window, min_periods=window).mean()
            return atr_series.iloc[-1]
        except Exception as e:
            self.logger.error(f"Error calculating single ATR: {e}")
            return float("nan")

    def _compute_range(self, df: pd.DataFrame) -> float:
        try:
            if len(df) < 1:
                self.logger.warning("Not enough data to compute range.")
                return float("nan")
            high = df[FeatureEngineeringColumns.HIGH_PRICE].iloc[-1]
            low = df[FeatureEngineeringColumns.LOW_PRICE].iloc[-1]
            return high - low
        except Exception as e:
            self.logger.error(f"Error calculating single range: {e}")
            return float("nan")

    def _compute_body(self, df: pd.DataFrame) -> float:
        try:
            if len(df) < 1:
                self.logger.warning("Not enough data to compute body.")
                return float("nan")
            close = df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-1]
            open_ = df[FeatureEngineeringColumns.OPEN_PRICE].iloc[-1]
            return abs(close - open_)
        except Exception as e:
            self.logger.error(f"Error calculating single body: {e}")
            return float("nan")

    def _compute_upper_wick(self, df: pd.DataFrame) -> float:
        try:
            if len(df) < 1:
                self.logger.warning("Not enough data to compute upper wick.")
                return float("nan")
            high = df[FeatureEngineeringColumns.HIGH_PRICE].iloc[-1]
            open_ = df[FeatureEngineeringColumns.OPEN_PRICE].iloc[-1]
            close = df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-1]
            return high - max(open_, close)
        except Exception as e:
            self.logger.error(f"Error calculating single upper wick: {e}")
            return float("nan")

    def _compute_lower_wick(self, df: pd.DataFrame) -> float:
        try:
            if len(df) < 1:
                self.logger.warning("Not enough data to compute lower wick.")
                return float("nan")
            open_ = df[FeatureEngineeringColumns.OPEN_PRICE].iloc[-1]
            close = df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-1]
            low = df[FeatureEngineeringColumns.LOW_PRICE].iloc[-1]
            return min(open_, close) - low
        except Exception as e:
            self.logger.error(f"Error calculating single lower wick: {e}")
            return float("nan")

    def _compute_volume_ma(self, df: pd.DataFrame, window: int) -> float:
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute volume MA for window {window}."
            )
            return float("nan")
        try:
            vol_ma_series = (
                df[FeatureEngineeringColumns.VOLUME].rolling(window=window).mean()
            )
            return vol_ma_series.iloc[-1]
        except Exception as e:
            self.logger.error(
                f"Error computing single volume MA for window {window}: {e}"
            )
            return float("nan")

    def _compute_vol_change(self, df: pd.DataFrame) -> float:
        if len(df) < 2:
            self.logger.warning("Not enough data to compute volume change.")
            return float("nan")
        try:
            prev = df[FeatureEngineeringColumns.VOLUME].iloc[-2]
            curr = df[FeatureEngineeringColumns.VOLUME].iloc[-1]
            return (curr - prev) / prev if prev != 0 else float("nan")
        except Exception as e:
            self.logger.error(f"Error computing single volume change: {e}")
            return float("nan")

    def _compute_vwap(self, df: pd.DataFrame, window: int) -> float:
        if len(df) < window:
            self.logger.warning(f"Not enough data to compute VWAP for window {window}.")
            return float("nan")
        try:
            vwap_series = (
                df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
                * df[FeatureEngineeringColumns.VOLUME]
            ).rolling(window=window).sum() / df[
                FeatureEngineeringColumns.VOLUME
            ].rolling(window=window).sum()
            return vwap_series.iloc[-1].replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(f"Error computing single VWAP for window {window}: {e}")
            return float("nan")

    def _compute_hour(self, df: pd.DataFrame) -> float:
        if FeatureEngineeringColumns.TIMESTAMP not in df.columns:
            self.logger.warning("Timestamp column is missing.")
            return float("nan")
        try:
            ts = df[FeatureEngineeringColumns.TIMESTAMP].iloc[-1]
            # If ts is a pandas Timestamp, get hour directly
            if hasattr(ts, "hour"):
                return float(ts.hour)
            # If ts is a datetime string, convert to pandas Timestamp
            ts = pd.to_datetime(ts)
            return float(ts.hour)
        except Exception as e:
            self.logger.error(f"Error computing single hour: {e}")
            return float("nan")

    def _compute_day_of_week(self, df: pd.DataFrame) -> float:
        if FeatureEngineeringColumns.TIMESTAMP not in df.columns:
            self.logger.warning("Timestamp column is missing.")
            return float("nan")
        try:
            ts = df[FeatureEngineeringColumns.TIMESTAMP].iloc[-1]
            if hasattr(ts, "dayofweek"):
                return float(ts.dayofweek)
            ts = pd.to_datetime(ts)
            return float(ts.dayofweek)
        except Exception as e:
            self.logger.error(f"Error computing single day of week: {e}")
            return float("nan")

    def _compute_adx(self, df, window=14) -> float:
        try:
            if len(df) < window:
                self.logger.warning(
                    f"Not enough data to compute ADX for window {window}."
                )
                return float("nan")
            high = df[FeatureEngineeringColumns.HIGH_PRICE]
            low = df[FeatureEngineeringColumns.LOW_PRICE]
            close = df[FeatureEngineeringColumns.CLOSE_PRICE]
            plus_dm = high.diff()
            minus_dm = low.diff().abs()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=window, min_periods=window).mean()
            plus_di = 100 * (
                plus_dm.rolling(window=window, min_periods=window).mean() / atr
            )
            minus_di = 100 * (
                minus_dm.rolling(window=window, min_periods=window).mean() / atr
            )
            dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
            adx_series = dx.rolling(window=window, min_periods=window).mean()
            return adx_series.iloc[-1].replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(f"Error calculating single ADX: {e}")
            return float("nan")

    def _compute_momentum(self, df: pd.DataFrame, window: int) -> float:
        if FeatureEngineeringColumns.CLOSE_PRICE not in df.columns:
            self.logger.warning("Close price column is missing.")
            return float("nan")
        if len(df) < window + 1:
            self.logger.warning(
                f"Not enough data to compute momentum for window {window}."
            )
            return float("nan")
        try:
            momentum_series = df[FeatureEngineeringColumns.CLOSE_PRICE].diff(
                periods=window
            )
            return momentum_series.iloc[-1]
        except Exception as e:
            self.logger.error(f"Error computing single momentum: {e}")
            return float("nan")

    def _compute_roc(self, df: pd.DataFrame, window: int) -> float:
        if FeatureEngineeringColumns.CLOSE_PRICE not in df.columns:
            self.logger.warning("Close price column is missing.")
            return float("nan")
        if len(df) < window + 1:
            self.logger.warning(f"Not enough data to compute ROC for window {window}.")
            return float("nan")
        try:
            roc_series = df[FeatureEngineeringColumns.CLOSE_PRICE].pct_change(
                periods=window
            )
            return roc_series.iloc[-1]
        except Exception as e:
            self.logger.error(f"Error computing single ROC: {e}")
            return float("nan")

    def _compute_stochastic_k(self, df: pd.DataFrame, window: int = 14) -> float:
        if len(df) < window:
            self.logger.warning("DataFrame is shorter than the window.")
            return float("nan")
        if (
            FeatureEngineeringColumns.HIGH_PRICE not in df.columns
            or FeatureEngineeringColumns.LOW_PRICE not in df.columns
            or FeatureEngineeringColumns.CLOSE_PRICE not in df.columns
        ):
            self.logger.warning("High, low, or close price columns are missing.")
            return float("nan")
        try:
            high = df[FeatureEngineeringColumns.HIGH_PRICE]
            low = df[FeatureEngineeringColumns.LOW_PRICE]
            close = df[FeatureEngineeringColumns.CLOSE_PRICE]
            stoch_k_series = (
                (close - low.rolling(window=window).min())
                / (high.rolling(window=window).max() - low.rolling(window=window).min())
                * 100
            )
            return stoch_k_series.iloc[-1].replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(f"Error computing single Stochastic K: {e}")
            return float("nan")

    def _compute_stochastic_d(self, df: pd.DataFrame, window: int = 3) -> float:
        if len(df) < window:
            self.logger.warning("DataFrame is shorter than the window.")
            return float("nan")
        if FeatureEngineeringColumns.STOCHASTIC_K not in df.columns:
            self.logger.warning("Stochastic K column is missing.")
            return float("nan")
        try:
            stoch_d_series = (
                df[FeatureEngineeringColumns.STOCHASTIC_K].rolling(window=window).mean()
            )
            return stoch_d_series.iloc[-1]
        except Exception as e:
            self.logger.error(f"Error computing single Stochastic D: {e}")
            return float("nan")

    def _compute_bollinger_upper(self, df: pd.DataFrame, window: int = 20) -> float:
        if FeatureEngineeringColumns.CLOSE_PRICE not in df.columns:
            self.logger.warning("Close price column is missing.")
            return float("nan")
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute Bollinger Upper Band for window {window}."
            )
            return float("nan")
        try:
            sma = (
                df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).mean()
            )
            std = df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).std()
            upper_series = sma + (std * 2)
            return upper_series.iloc[-1]
        except Exception as e:
            self.logger.error(f"Error computing single Bollinger Upper Band: {e}")
            return float("nan")

    def _compute_bollinger_lower(self, df: pd.DataFrame, window: int = 20) -> float:
        if FeatureEngineeringColumns.CLOSE_PRICE not in df.columns:
            self.logger.warning("Close price column is missing.")
            return float("nan")
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute Bollinger Lower Band for window {window}."
            )
            return float("nan")
        try:
            sma = (
                df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).mean()
            )
            std = df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).std()
            lower_series = sma - (std * 2)
            return lower_series.iloc[-1]
        except Exception as e:
            self.logger.error(f"Error computing single Bollinger Lower Band: {e}")
            return float("nan")

    def _compute_bollinger_width(self, df: pd.DataFrame, window: int = 20) -> float:
        if (
            FeatureEngineeringColumns.BOLLINGER_UPPER not in df.columns
            or FeatureEngineeringColumns.BOLLINGER_LOWER not in df.columns
        ):
            self.logger.warning("Bollinger Bands columns are missing.")
            return float("nan")
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute Bollinger Width for window {window}."
            )
            return float("nan")
        try:
            sma = (
                df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).mean()
            )
            width_series = (
                df[FeatureEngineeringColumns.BOLLINGER_UPPER]
                - df[FeatureEngineeringColumns.BOLLINGER_LOWER]
            ) / sma
            return width_series.iloc[-1].replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(f"Error computing single Bollinger Width: {e}")
            return float("nan")

    def _compute_gap(self, df: pd.DataFrame) -> float:
        if (
            FeatureEngineeringColumns.CLOSE_PRICE not in df.columns
            or FeatureEngineeringColumns.OPEN_PRICE not in df.columns
        ):
            self.logger.warning("Close or Open price columns are missing.")
            return float("nan")
        if len(df) < 1:
            self.logger.warning("Not enough data to compute gap.")
            return float("nan")
        try:
            close = df[FeatureEngineeringColumns.CLOSE_PRICE].iloc[-1]
            open_ = df[FeatureEngineeringColumns.OPEN_PRICE].iloc[-1]
            gap = (close - open_) / open_
            return gap.replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(f"Error computing single Gap: {e}")
            return float("nan")

    def _compute_high_low_ratio(self, df: pd.DataFrame) -> float:
        if (
            FeatureEngineeringColumns.HIGH_PRICE not in df.columns
            or FeatureEngineeringColumns.LOW_PRICE not in df.columns
        ):
            self.logger.warning("High/Low price columns are missing.")
            return float("nan")
        try:
            high_price = df[FeatureEngineeringColumns.HIGH_PRICE].iloc[-1]
            low_price = df[FeatureEngineeringColumns.LOW_PRICE].iloc[-1]
            ratio = high_price / low_price
            return ratio.replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(f"Error computing High/Low Ratio: {e}")
            return float("nan")

    def _compute_obv(self, df: pd.DataFrame) -> float:
        if (
            FeatureEngineeringColumns.CLOSE_PRICE not in df.columns
            or FeatureEngineeringColumns.VOLUME not in df.columns
        ):
            self.logger.warning("Close price or Volume columns are missing.")
            return float("nan")
        try:
            obv = (
                (
                    df[FeatureEngineeringColumns.VOLUME]
                    * np.sign(df[FeatureEngineeringColumns.CLOSE_PRICE].diff())
                )
                .fillna(0)
                .cumsum()
            )
            return obv.iloc[-1].replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(f"Error computing On-Balance Volume (OBV): {e}")
            return float("nan")

    def _compute_adl(self, df: pd.DataFrame) -> float:
        if (
            FeatureEngineeringColumns.CLOSE_PRICE not in df.columns
            or FeatureEngineeringColumns.VOLUME not in df.columns
            or FeatureEngineeringColumns.HIGH_PRICE not in df.columns
            or FeatureEngineeringColumns.LOW_PRICE not in df.columns
        ):
            self.logger.warning(
                "Close price, Volume, High price or Low price columns are missing."
            )
            return float("nan")
        try:
            adl = (
                (
                    df[FeatureEngineeringColumns.VOLUME]
                    * (
                        df[FeatureEngineeringColumns.CLOSE_PRICE]
                        - df[FeatureEngineeringColumns.LOW_PRICE]
                    )
                    / (
                        df[FeatureEngineeringColumns.HIGH_PRICE]
                        - df[FeatureEngineeringColumns.LOW_PRICE]
                    )
                )
                .fillna(0)
                .cumsum()
            )
            return adl.iloc[-1].replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            self.logger.error(
                f"Error computing Accumulation/Distribution Line (ADL): {e}"
            )
            return float("nan")

    def _compute_timestamp(self, df: pd.DataFrame) -> float:
        if FeatureEngineeringColumns.TIMESTAMP not in df.columns:
            self.logger.warning("Timestamp column is missing.")
            return float("nan")
        try:
            ts = df[FeatureEngineeringColumns.TIMESTAMP].iloc[-1]
            # Ensure the returned value is a pandas Timestamp
            return pd.to_datetime(ts)
        except Exception as e:
            self.logger.error(f"Error computing Timestamp: {e}")
            return float("nan")

    def enrich_data(self, df: pd.DataFrame, logger: Loggable) -> pd.Series:
        try:
            logger.info(
                f"Input DataFrame shape: {df.shape}, columns: {list(df.columns)}"
            )
            last_row = df.copy().iloc[-1]
            # Price returns
            last_row[FeatureEngineeringColumns.PCT_RETURN] = self._compute_pct_return(
                df
            )
            last_row[FeatureEngineeringColumns.LOG_RETURN] = self._compute_log_return(
                df
            )

            # Moving averages (loop for brevity)
            for window in [10, 20, 50, 100, 150, 200]:
                last_row[getattr(FeatureEngineeringColumns, f"SMA_{window}")] = (
                    self._compute_sma(df, window)
                )
            for window in [9, 10, 12, 20, 26, 50, 100, 150, 200]:
                last_row[getattr(FeatureEngineeringColumns, f"EMA_{window}")] = (
                    self._compute_ema(df, window)
                )

            # MACD
            last_row[FeatureEngineeringColumns.MACD] = self._compute_macd(df)
            last_row[FeatureEngineeringColumns.MACD_SIGNAL] = self._compute_macd_signal(
                df
            )
            last_row[FeatureEngineeringColumns.RSI] = self._compute_rsi(df)

            # Volatility
            for window in [10, 20, 50]:
                last_row[getattr(FeatureEngineeringColumns, f"VOLATILITY_{window}")] = (
                    self._compute_volatility(df, window)
                )
            last_row[FeatureEngineeringColumns.HIST_VOLATILITY_20] = (
                self._compute_hist_volatility(df, window=20)
            )

            # ATR
            last_row[FeatureEngineeringColumns.ATR_14] = self._compute_atr(
                df, window=14
            )

            # Range and candle features
            last_row[FeatureEngineeringColumns.RANGE] = self._compute_range(df)
            last_row[FeatureEngineeringColumns.BODY] = self._compute_body(df)
            last_row[FeatureEngineeringColumns.UPPER_WICK] = self._compute_upper_wick(
                df
            )
            last_row[FeatureEngineeringColumns.LOWER_WICK] = self._compute_lower_wick(
                df
            )

            # Volume features
            for window in [10, 20, 50, 100, 200]:
                last_row[getattr(FeatureEngineeringColumns, f"VOL_MA_{window}")] = (
                    self._compute_volume_ma(df, window)
                )
            last_row[FeatureEngineeringColumns.VOL_CHANGE] = self._compute_vol_change(
                df
            )

            # VWAP rolling
            for window in [10, 20, 50, 100, 150, 200]:
                last_row[getattr(FeatureEngineeringColumns, f"VWAP_{window}")] = (
                    self._compute_vwap(df, window)
                )

            # Time features
            last_row[FeatureEngineeringColumns.HOUR] = self._compute_hour(df)
            last_row[FeatureEngineeringColumns.DAY_OF_WEEK] = self._compute_day_of_week(
                df
            )

            # ADX
            last_row[FeatureEngineeringColumns.ADX] = self._compute_adx(df, window=14)

            # Momentum, ROC
            for window in [10]:
                last_row[getattr(FeatureEngineeringColumns, f"MOMENTUM_{window}")] = (
                    self._compute_momentum(df, window)
                )
            for window in [10]:
                last_row[getattr(FeatureEngineeringColumns, f"ROC_{window}")] = (
                    self._compute_roc(df, window)
                )

            # Stochastic K/D
            last_row[FeatureEngineeringColumns.STOCHASTIC_K] = (
                self._compute_stochastic_k(df, window=14)
            )
            last_row[FeatureEngineeringColumns.STOCHASTIC_D] = (
                self._compute_stochastic_d(df, window=3)
            )

            # Bollinger Bands
            last_row[FeatureEngineeringColumns.BOLLINGER_UPPER] = (
                self._compute_bollinger_upper(df)
            )
            last_row[FeatureEngineeringColumns.BOLLINGER_LOWER] = (
                self._compute_bollinger_lower(df)
            )
            last_row[FeatureEngineeringColumns.BOLLINGER_WIDTH] = (
                self._compute_bollinger_width(df)
            )

            # GAP, High/Low Ratio
            last_row[FeatureEngineeringColumns.GAP] = self._compute_gap(df)

            last_row[FeatureEngineeringColumns.HIGH_LOW_RATIO] = (
                self._compute_high_low_ratio(df)
            )

            # OBV
            last_row[FeatureEngineeringColumns.OBV] = self._compute_obv

            # ADL
            last_row[FeatureEngineeringColumns.ADL] = self._compute_adl(df)

            # Ensure timestamp is datetime
            last_row[FeatureEngineeringColumns.TIMESTAMP] = self._compute_timestamp(df)

            # Validation: ensure all features in FeatureEngineeringColumns are present in the last row
            missing = [
                getattr(FeatureEngineeringColumns, attr)
                for attr in dir(FeatureEngineeringColumns)
                if not attr.startswith("__")
                and not callable(getattr(FeatureEngineeringColumns, attr))
                and getattr(FeatureEngineeringColumns, attr) not in last_row.index
            ]
            if missing:
                logger.error(
                    f"Missing features in last row after engineering: {missing}"
                )
                raise ValueError(
                    f"Missing features in last row after engineering: {missing}"
                )

            return last_row
        except Exception as e:
            logger.error(f"Feature engineering failed: {e}")
            raise ValueError(f"Feature engineering failed: {e}") from e
