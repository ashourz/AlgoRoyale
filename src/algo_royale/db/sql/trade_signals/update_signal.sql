
UPDATE trade_signals
SET symbol = %s, signal = %s, price = %s, created_at = %s
WHERE id = %s;
