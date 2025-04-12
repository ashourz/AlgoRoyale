-- db\sql\trade_signals\get_signals_by_symbol.sql

-- This SQL query retrieves the most recent trade signal for a specific symbol from the trade_signals table.
SELECT * FROM trade_signals
WHERE symbol = %s
AND created_at >= %s
AND created_at <= %s
ORDER BY created_at DESC;