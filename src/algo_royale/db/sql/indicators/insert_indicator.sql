-- db\sql\indicators\insert_indicator.sql

-- This SQL query retrieves all indicators associated with a specific trade ID from the indicators table.
-- It orders the results by the recorded_at timestamp in descending order.
INSERT INTO indicators (trade_id, rsi, macd, macd_signal, volume, bollinger_upper, bollinger_lower, atr, price, ema_short, ema_long, recorded_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())