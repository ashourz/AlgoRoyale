-- db\sql\trades\get_trades_by_symbol_and_date.sql

-- This SQL query retrieves all trades for a specific symbol within a given date range, ordered by entry time in descending order.
SELECT * FROM trades 
WHERE symbol = %s AND entry_time BETWEEN %s AND %s 
ORDER BY entry_time DESC;