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

    def _compute_pct_return(self, df: pd.DataFrame) -> pd.Series:
        if len(df) < 2:
            self.logger.warning("Not enough data to compute percent return.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.CLOSE_PRICE].pct_change()
        except Exception as e:
            self.logger.error(f"Error computing percent return: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_log_return(self, df: pd.DataFrame) -> pd.Series:
        if len(df) < 2:
            self.logger.warning("Not enough data to compute log return.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return np.log(df[FeatureEngineeringColumns.CLOSE_PRICE]).diff()
        except Exception as e:
            self.logger.error(f"Error computing log return: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_sma(self, df: pd.DataFrame, window: int) -> pd.Series:
        if len(df) < window:
            self.logger.warning(f"Not enough data to compute SMA for window {window}.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return (
                df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).mean()
            )
        except Exception as e:
            self.logger.error(f"Error computing SMA for window {window}: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_ema(self, df: pd.DataFrame, window: int) -> pd.Series:
        if len(df) < window:
            self.logger.warning(f"Not enough data to compute EMA for window {window}.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return (
                df[FeatureEngineeringColumns.CLOSE_PRICE]
                .ewm(span=window, adjust=False)
                .mean()
            )
        except Exception as e:
            self.logger.error(f"Error computing EMA for window {window}: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_macd(self, df: pd.DataFrame) -> pd.Series:
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
            return ema_12 - ema_26
        except Exception as e:
            self.logger.error(f"Error computing MACD: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_macd_signal(self, df: pd.DataFrame) -> pd.Series:
        try:
            return df[FeatureEngineeringColumns.MACD].ewm(span=9, adjust=False).mean()
        except Exception as e:
            self.logger.error(f"Error computing MACD signal: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_rsi(self, df: pd.DataFrame, window=14) -> pd.Series:
        try:
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
            return 100 - (100 / (1 + rs))
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_volatility(self, df: pd.DataFrame, window: int) -> pd.Series:
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute volatility for window {window}."
            )
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.PCT_RETURN].rolling(window=window).std()
        except Exception as e:
            self.logger.error(f"Error computing volatility for window {window}: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_hist_volatility(self, df: pd.DataFrame, window: int) -> pd.Series:
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute historical volatility for window {window}."
            )
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.PCT_RETURN].rolling(
                window=window
            ).std() * np.sqrt(252)
        except Exception as e:
            self.logger.error(
                f"Error computing historical volatility for window {window}: {e}"
            )
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_atr(self, df: pd.DataFrame, window=14) -> pd.Series:
        try:
            high = df[FeatureEngineeringColumns.HIGH_PRICE]
            low = df[FeatureEngineeringColumns.LOW_PRICE]
            close = df[FeatureEngineeringColumns.CLOSE_PRICE]
            tr = pd.concat(
                [high - low, (high - close.shift()).abs(), (low - close.shift()).abs()],
                axis=1,
            ).max(axis=1)
            return tr.rolling(window=window, min_periods=window).mean()
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_range(self, df: pd.DataFrame) -> pd.Series:
        try:
            return (
                df[FeatureEngineeringColumns.HIGH_PRICE]
                - df[FeatureEngineeringColumns.LOW_PRICE]
            )
        except Exception as e:
            self.logger.error(f"Error calculating range: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_body(self, df: pd.DataFrame) -> pd.Series:
        try:
            return abs(
                df[FeatureEngineeringColumns.CLOSE_PRICE]
                - df[FeatureEngineeringColumns.OPEN_PRICE]
            )
        except Exception as e:
            self.logger.error(f"Error calculating body: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_upper_wick(self, df: pd.DataFrame) -> pd.Series:
        try:
            return df[FeatureEngineeringColumns.HIGH_PRICE] - df[
                [
                    FeatureEngineeringColumns.OPEN_PRICE,
                    FeatureEngineeringColumns.CLOSE_PRICE,
                ]
            ].max(axis=1)
        except Exception as e:
            self.logger.error(f"Error calculating upper wick: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_lower_wick(self, df: pd.DataFrame) -> pd.Series:
        try:
            return (
                df[
                    [
                        FeatureEngineeringColumns.OPEN_PRICE,
                        FeatureEngineeringColumns.CLOSE_PRICE,
                    ]
                ].min(axis=1)
                - df[FeatureEngineeringColumns.LOW_PRICE]
            )
        except Exception as e:
            self.logger.error(f"Error calculating lower wick: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_volume_ma(self, df: pd.DataFrame, window: int) -> pd.Series:
        if len(df) < window:
            self.logger.warning(
                f"Not enough data to compute volume MA for window {window}."
            )
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.VOLUME].rolling(window=window).mean()
        except Exception as e:
            self.logger.error(f"Error computing volume MA for window {window}: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_vol_change(self, df: pd.DataFrame) -> pd.Series:
        if len(df) < 2:
            self.logger.warning("Not enough data to compute volume change.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.VOLUME].pct_change()
        except Exception as e:
            self.logger.error(f"Error computing volume change: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_vwap(self, df: pd.DataFrame, window: int) -> pd.Series:
        if len(df) < window:
            self.logger.warning(f"Not enough data to compute VWAP for window {window}.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            vwap = (
                df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
                * df[FeatureEngineeringColumns.VOLUME]
            ).rolling(window=window).sum() / df[
                FeatureEngineeringColumns.VOLUME
            ].rolling(window=window).sum()
            return vwap
        except Exception as e:
            self.logger.error(f"Error computing VWAP for window {window}: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_hour(self, df: pd.DataFrame) -> pd.Series:
        if FeatureEngineeringColumns.TIMESTAMP not in df.columns:
            self.logger.warning("Timestamp column is missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.TIMESTAMP].dt.hour
        except Exception as e:
            self.logger.error(f"Error computing hour: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_day_of_week(self, df: pd.DataFrame) -> pd.Series:
        if FeatureEngineeringColumns.TIMESTAMP not in df.columns:
            self.logger.warning("Timestamp column is missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.TIMESTAMP].dt.dayofweek
        except Exception as e:
            self.logger.error(f"Error computing day of week: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_adx(self, df, window=14) -> pd.Series:
        try:
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
            adx = dx.rolling(window=window, min_periods=window).mean()
            return adx
        except Exception as e:
            self.logger.error(f"Error calculating ADX: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_momentum(self, df: pd.DataFrame, window: int) -> pd.Series:
        if FeatureEngineeringColumns.CLOSE_PRICE not in df.columns:
            self.logger.warning("Close price column is missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.CLOSE_PRICE].diff(periods=window)
        except Exception as e:
            self.logger.error(f"Error computing momentum: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_roc(self, df: pd.DataFrame, window: int) -> pd.Series:
        if FeatureEngineeringColumns.CLOSE_PRICE not in df.columns:
            self.logger.warning("Close price column is missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return df[FeatureEngineeringColumns.CLOSE_PRICE].pct_change(periods=window)
        except Exception as e:
            self.logger.error(f"Error computing ROC: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_stochastic_k(self, df: pd.DataFrame, window: int = 14) -> pd.Series:
        if len(df) < window:
            self.logger.warning("DataFrame is shorter than the window.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        if (
            FeatureEngineeringColumns.HIGH_PRICE not in df.columns
            or FeatureEngineeringColumns.LOW_PRICE not in df.columns
            or FeatureEngineeringColumns.CLOSE_PRICE not in df.columns
        ):
            self.logger.warning("High, low, or close price columns are missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            high = df[FeatureEngineeringColumns.HIGH_PRICE]
            low = df[FeatureEngineeringColumns.LOW_PRICE]
            close = df[FeatureEngineeringColumns.CLOSE_PRICE]
            stoch_k = (
                (close - low.rolling(window=window).min())
                / (high.rolling(window=window).max() - low.rolling(window=window).min())
                * 100
            )
            return stoch_k
        except Exception as e:
            self.logger.error(f"Error computing Stochastic K: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_stochastic_d(self, df: pd.DataFrame, window: int = 3) -> pd.Series:
        if len(df) < window:
            self.logger.warning("DataFrame is shorter than the window.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        if FeatureEngineeringColumns.STOCHASTIC_K not in df.columns:
            self.logger.warning("Stochastic K column is missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return (
                df[FeatureEngineeringColumns.STOCHASTIC_K].rolling(window=window).mean()
            )
        except Exception as e:
            self.logger.error(f"Error computing Stochastic D: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_bollinger_upper(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        if FeatureEngineeringColumns.CLOSE_PRICE not in df.columns:
            self.logger.warning("Close price column is missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            sma = (
                df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).mean()
            )
            std = df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).std()
            return sma + (std * 2)
        except Exception as e:
            self.logger.error(f"Error computing Bollinger Upper Band: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_bollinger_lower(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        if FeatureEngineeringColumns.CLOSE_PRICE not in df.columns:
            self.logger.warning("Close price column is missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            sma = (
                df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).mean()
            )
            std = df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).std()
            return sma - (std * 2)
        except Exception as e:
            self.logger.error(f"Error computing Bollinger Lower Band: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_bollinger_width(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        if (
            FeatureEngineeringColumns.BOLLINGER_UPPER not in df.columns
            or FeatureEngineeringColumns.BOLLINGER_LOWER not in df.columns
        ):
            self.logger.warning("Bollinger Bands columns are missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            sma = (
                df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).mean()
            )
            return (
                df[FeatureEngineeringColumns.BOLLINGER_UPPER]
                - df[FeatureEngineeringColumns.BOLLINGER_LOWER]
            ) / sma
        except Exception as e:
            self.logger.error(f"Error computing Bollinger Width: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

    def _compute_gap(self, df: pd.DataFrame) -> pd.Series:
        if (
            FeatureEngineeringColumns.CLOSE_PRICE not in df.columns
            or FeatureEngineeringColumns.OPEN_PRICE not in df.columns
        ):
            self.logger.warning("Bollinger Bands columns are missing.")
            return pd.Series([float("nan")] * len(df), index=df.index)
        try:
            return (
                df[FeatureEngineeringColumns.CLOSE_PRICE]
                - df[FeatureEngineeringColumns.OPEN_PRICE]
            )
        except Exception as e:
            self.logger.error(f"Error computing Gap: {e}")
            return pd.Series([float("nan")] * len(df), index=df.index)

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
            return high_price / low_price if low_price != 0 else 0
        except Exception as e:
            self.logger.error(f"Error computing High/Low Ratio: {e}")
            return float("nan")

    def enrich_data(self, df: pd.DataFrame, logger: Loggable) -> pd.DataFrame:
        try:
            logger.info(
                f"Input DataFrame shape: {df.shape}, columns: {list(df.columns)}"
            )

            # Price returns
            df[FeatureEngineeringColumns.PCT_RETURN] = self._compute_pct_return(df)
            df[FeatureEngineeringColumns.LOG_RETURN] = self._compute_log_return(df)

            # Moving averages (loop for brevity)
            for window in [10, 20, 50, 100, 150, 200]:
                df[getattr(FeatureEngineeringColumns, f"SMA_{window}")] = (
                    self._compute_sma(df, window)
                )
            for window in [9, 10, 12, 20, 26, 50, 100, 150, 200]:
                df[getattr(FeatureEngineeringColumns, f"EMA_{window}")] = (
                    self._compute_ema(df, window)
                )

            # MACD
            df[FeatureEngineeringColumns.MACD] = self._compute_macd(df)
            df[FeatureEngineeringColumns.MACD_SIGNAL] = self._compute_macd_signal(df)
            # RSI
            df[FeatureEngineeringColumns.RSI] = self._compute_rsi(df)

            # Volatility
            for window in [10, 20, 50]:
                df[getattr(FeatureEngineeringColumns, f"VOLATILITY_{window}")] = (
                    self._compute_volatility(df, window)
                )
            df[FeatureEngineeringColumns.HIST_VOLATILITY_20] = (
                self._compute_hist_volatility(df, window=20)
            )

            # ATR
            df[FeatureEngineeringColumns.ATR_14] = self._compute_atr(df, window=14)

            # Range and candle features
            df[FeatureEngineeringColumns.RANGE] = self._compute_range(df)
            df[FeatureEngineeringColumns.BODY] = self._compute_body(df)
            df[FeatureEngineeringColumns.UPPER_WICK] = self._compute_upper_wick(df)
            df[FeatureEngineeringColumns.LOWER_WICK] = self._compute_lower_wick(df)

            # Volume features
            for window in [10, 20, 50, 100, 200]:
                df[getattr(FeatureEngineeringColumns, f"VOL_MA_{window}")] = (
                    self._compute_volume_ma(df, window)
                )
            df[FeatureEngineeringColumns.VOL_CHANGE] = self._compute_vol_change(df)

            # VWAP rolling
            for window in [10, 20, 50, 100, 150, 200]:
                df[getattr(FeatureEngineeringColumns, f"VWAP_{window}")] = (
                    self._compute_vwap(df, window)
                )

            # Time features
            df[FeatureEngineeringColumns.HOUR] = self._compute_hour(df)
            df[FeatureEngineeringColumns.DAY_OF_WEEK] = self._compute_day_of_week(df)

            # ADX
            df[FeatureEngineeringColumns.ADX] = self._compute_adx(df, window=14)

            # Momentum, ROC
            for window in [10]:
                df[getattr(FeatureEngineeringColumns, f"MOMENTUM_{window}")] = (
                    self._compute_momentum(df, window)
                )
            for window in [10]:
                df[getattr(FeatureEngineeringColumns, f"ROC_{window}")] = (
                    self._compute_roc(df, window)
                )

            # Stochastic K/D
            df[FeatureEngineeringColumns.STOCHASTIC_K] = self._compute_stochastic_k(
                df, window=14
            )
            df[FeatureEngineeringColumns.STOCHASTIC_D] = self._compute_stochastic_d(
                df, window=3
            )

            # Bollinger Bands
            df[FeatureEngineeringColumns.BOLLINGER_UPPER] = (
                self._compute_bollinger_upper(df)
            )
            df[FeatureEngineeringColumns.BOLLINGER_LOWER] = (
                self._compute_bollinger_lower(df)
            )
            df[FeatureEngineeringColumns.BOLLINGER_WIDTH] = (
                self._compute_bollinger_width(df)
            )

            # GAP, High/Low Ratio
            df[FeatureEngineeringColumns.GAP] = (
                df[FeatureEngineeringColumns.CLOSE_PRICE]
                - df[FeatureEngineeringColumns.OPEN_PRICE]
            ) / df[FeatureEngineeringColumns.OPEN_PRICE]
            df[FeatureEngineeringColumns.HIGH_LOW_RATIO] = (
                df[FeatureEngineeringColumns.HIGH_PRICE]
                / df[FeatureEngineeringColumns.LOW_PRICE]
            ).replace([np.inf, -np.inf], np.nan)

            # OBV
            df[FeatureEngineeringColumns.OBV] = (
                (
                    df[FeatureEngineeringColumns.VOLUME]
                    * np.sign(df[FeatureEngineeringColumns.CLOSE_PRICE].diff())
                )
                .fillna(0)
                .cumsum()
            )

            # ADL
            df[FeatureEngineeringColumns.ADL] = (
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
                ).fillna(0)
            ).cumsum()

            # Ensure timestamp is datetime
            df[FeatureEngineeringColumns.TIMESTAMP] = pd.to_datetime(
                df[FeatureEngineeringColumns.TIMESTAMP]
            )

            logger.info(f"DataFrame shape before dropna: {df.shape}")
            logger.info(
                f"DataFrame columns after feature engineering: {list(df.columns)}"
            )

            # Validation: ensure all features in FeatureEngineeringColumns are present
            missing = [
                getattr(FeatureEngineeringColumns, attr)
                for attr in dir(FeatureEngineeringColumns)
                if not attr.startswith("__")
                and not callable(getattr(FeatureEngineeringColumns, attr))
                and getattr(FeatureEngineeringColumns, attr) not in df.columns
            ]
            if missing:
                logger.error(f"Missing features after engineering: {missing}")
                raise ValueError(f"Missing features after engineering: {missing}")

            logger.info(f"Feature engineering complete. Output shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Feature engineering failed: {e}")
            raise ValueError(f"Feature engineering failed: {e}") from e
