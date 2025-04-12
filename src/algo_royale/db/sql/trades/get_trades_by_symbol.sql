-- db\sql\trades\get_trades_page_by_symbol.sql
--
-- This SQL query retrieves the most recent trades for a specific symbol from the trades table.
SELECT * FROM trades
WHERE symbol = %s
ORDER BY entry_time DESC
LIMIT %s OFFSET %s;