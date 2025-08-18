from uuid import UUID

from pydantic import BaseModel


class DBEnrichedData(BaseModel):
    """Represents enriched data associated with an order in the Algo Royale system.
    Attributes:
        id (int): Unique identifier for the enriched data.
        order_id (int): ID of the associated order.
        market_timestamp (str): Timestamp of the market data.
        symbol (str): Trading symbol of the asset.
        market (str): Market where the data was collected.
        volume (float): Trading volume.
        open_price (float): Opening price of the asset.
        high_price (float): Highest price during the period.
        low_price (float): Lowest price during the period.
        close_price (float): Closing price of the asset.
        num_trades (int): Number of trades during the period.
        volume_weighted_price (float): Volume-weighted average price.
        pct_return (float): Percentage return.
        log_return (float): Logarithmic return.
        sma_10, sma_20, sma_50, sma_100, sma_150, sma_200 (float): Simple moving averages for different periods.
        macd, macd_signal (float): Moving Average Convergence Divergence values.
        rsi (float): Relative Strength Index value.
        ema_9, ema_10, ema_12, ema_20, ema_26, ema_50, ema_100, ema_150, ema_200 (float): Exponential moving averages for different periods.
        volatility_10, volatility_20, volatility_50 (float): Volatility measures for different periods.
        atr_14 (float): Average True Range over 14 periods.
        hist_volatility_20 (float): Historical volatility over 20 periods.
        range (float): Price range during the period.
        body, upper_wick, lower_wick (float): Candlestick components.
        vol_ma_10, vol_ma_20, vol_ma_50, vol_ma_100, vol_ma_200 (float): Volume moving averages for different periods.
        vol_change (float): Change in volume.
        vwap_10, vwap_20, vwap_50, vwap_100, vwap_150, vwap_200 (float): Volume-weighted average prices for different periods.
        hour (int): Hour of the day.
        day_of_week (int): Day of the week (0=Monday, 6=Sunday).
        adx (float): Average Directional Index.
        momentum_10 (float): Momentum over 10 periods.
        roc_10 (float): Rate of Change over 10 periods.
        stochastic_k (float): Stochastic %K value.
        stochastic_d (float): Stochastic %D value.
        bollinger_upper (float): Upper Bollinger Band.
        bollinger_lower (float): Lower Bollinger Band.
        bollinger_width (float): Bollinger Band width.
        gap (float): Price gap.
        high_low_ratio (float): High/Low price ratio.
        obv (float): On-Balance Volume.
        adl (float): Accumulation/Distribution Line.
    """

    id: UUID
    order_id: UUID
    market_timestamp: str
    symbol: str
    market: str
    volume: float
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    num_trades: int
    volume_weighted_price: float
    pct_return: float
    log_return: float
    sma_10: float
    sma_20: float
    sma_50: float
    sma_100: float
    sma_150: float
    sma_200: float
    macd: float
    macd_signal: float
    rsi: float
    ema_9: float
    ema_10: float
    ema_12: float
    ema_20: float
    ema_26: float
    ema_50: float
    ema_100: float
    ema_150: float
    ema_200: float
    volatility_10: float
    volatility_20: float
    volatility_50: float
    atr_14: float
    hist_volatility_20: float
    range: float
    body: float
    upper_wick: float
    lower_wick: float
    vol_ma_10: float
    vol_ma_20: float
    vol_ma_50: float
    vol_ma_100: float
    vol_ma_200: float
    vol_change: float
    vwap_10: float
    vwap_20: float
    vwap_50: float
    vwap_100: float
    vwap_150: float
    vwap_200: float
    hour: int
    day_of_week: int
    adx: float
    momentum_10: float
    roc_10: float
    stochastic_k: float
    stochastic_d: float
    bollinger_upper: float
    bollinger_lower: float
    bollinger_width: float
    gap: float
    high_low_ratio: float
    obv: float
    adl: float

    @classmethod
    def columns(cls):
        """Returns a list of column names for the enriched data."""
        return [
            "id",
            "order_id",
            "market_timestamp",
            "symbol",
            "market",
            "volume",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "num_trades",
            "volume_weighted_price",
            "pct_return",
            "log_return",
            "sma_10",
            "sma_20",
            "sma_50",
            "sma_100",
            "sma_150",
            "sma_200",
            "macd",
            "macd_signal",
            "rsi",
            "ema_9",
            "ema_10",
            "ema_12",
            "ema_20",
            "ema_26",
            "ema_50",
            "ema_100",
            "ema_150",
            "ema_200",
            "volatility_10",
            "volatility_20",
            "volatility_50",
            "atr_14",
            "hist_volatility_20",
            "range",
            "body",
            "upper_wick",
            "lower_wick",
            "vol_ma_10",
            "vol_ma_20",
            "vol_ma_50",
            "vol_ma_100",
            "vol_ma_200",
            "vol_change",
            "vwap_10",
            "vwap_20",
            "vwap_50",
            "vwap_100",
            "vwap_150",
            "vwap_200",
            "hour",
            "day_of_week",
            "adx",
            "momentum_10",
            "roc_10",
            "stochastic_k",
            "stochastic_d",
            "bollinger_upper",
            "bollinger_lower",
            "bollinger_width",
            "gap",
            "high_low_ratio",
            "obv",
            "adl",
        ]

    @classmethod
    def from_tuple(cls, data: tuple) -> "DBEnrichedData":
        """
        Creates a DBEnrichedData object from raw data.

        Args:
            data (tuple): A tuple representing enriched data from the database.

        Returns:
            DBEnrichedData: An instance of DBEnrichedData with fields populated from the raw data.
        """
        d = dict(zip(cls.columns(), data))
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, data: dict) -> "DBEnrichedData":
        """
        Creates a DBEnrichedData object from raw data.

        Args:
            data (dict): A dictionary representing enriched data from the database.

        Returns:
            DBEnrichedData: An instance of DBEnrichedData with fields populated from the raw data.
        """
        return DBEnrichedData(
            id=data["id"],
            order_id=data["order_id"],
            market_timestamp=data["market_timestamp"],
            symbol=data["symbol"],
            market=data["market"],
            volume=data["volume"],
            open_price=data["open_price"],
            high_price=data["high_price"],
            low_price=data["low_price"],
            close_price=data["close_price"],
            num_trades=data["num_trades"],
            volume_weighted_price=data["volume_weighted_price"],
            pct_return=data["pct_return"],
            log_return=data["log_return"],
            sma_10=data["sma_10"],
            sma_20=data["sma_20"],
            sma_50=data["sma_50"],
            sma_100=data["sma_100"],
            sma_150=data["sma_150"],
            sma_200=data["sma_200"],
            macd=data["macd"],
            macd_signal=data["macd_signal"],
            rsi=data["rsi"],
            ema_9=data["ema_9"],
            ema_10=data["ema_10"],
            ema_12=data["ema_12"],
            ema_20=data["ema_20"],
            ema_26=data["ema_26"],
            ema_50=data["ema_50"],
            ema_100=data["ema_100"],
            ema_150=data["ema_150"],
            ema_200=data["ema_200"],
            volatility_10=data.get("volatility_10"),
            volatility_20=data.get("volatility_20"),
            volatility_50=data.get("volatility_50"),
            atr_14=data.get("atr_14"),
            hist_volatility_20=data.get("hist_volatility_20"),
            range=data.get("range"),
            body=data.get("body"),
            upper_wick=data.get("upper_wick"),
            lower_wick=data.get("lower_wick"),
            vol_ma_10=data.get("vol_ma_10"),
            vol_ma_20=data.get("vol_ma_20"),
            vol_ma_50=data.get("vol_ma_50"),
            vol_ma_100=data.get("vol_ma_100"),
            vol_ma_200=data.get("vol_ma_200"),
            vol_change=data.get("vol_change"),
            vwap_10=data.get("vwap_10"),
            vwap_20=data.get("vwap_20"),
            vwap_50=data.get("vwap_50"),
            vwap_100=data.get("vwap_100"),
            vwap_150=data.get("vwap_150"),
            vwap_200=data.get("vwap_200"),
            hour=data.get("hour"),
            day_of_week=data.get("day_of_week"),
            adx=data.get("adx"),
            momentum_10=data.get("momentum_10"),
            roc_10=data.get("roc_10"),
            stochastic_k=data.get("stochastic_k"),
            stochastic_d=data.get("stochastic_d"),
            bollinger_upper=data.get("bollinger_upper"),
            bollinger_lower=data.get("bollinger_lower"),
            bollinger_width=data.get("bollinger_width"),
            gap=data.get("gap"),
            high_low_ratio=data.get("high_low_ratio"),
            obv=data.get("obv"),
            adl=data.get("adl"),
        )
