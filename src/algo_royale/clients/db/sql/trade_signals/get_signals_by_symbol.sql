-- db\sql\trade_signals\get_signals_by_symbol.sql

-- This SQL query retrieves the most recent trade signal for a specific symbol from the trade_signals table.
SELECT * FROM trade_signals
WHERE symbol = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;