
UPDATE indicators
SET rsi = %s, macd = %s, macd_signal = %s, volume = %s, bollinger_upper = %s, bollinger_lower = %s, atr = %s, price = %s, ema_short = %s, ema_long = %s, recorded_at = %s
WHERE id = %s;
