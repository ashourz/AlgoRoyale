-- db\sql\trades\get_recent_trades.sql
--
-- This SQL query retrieves the most recent trades for a specific symbol from the trades table.
SELECT * FROM trades
WHERE symbol = %s
ORDER BY trade_time DESC
LIMIT %s