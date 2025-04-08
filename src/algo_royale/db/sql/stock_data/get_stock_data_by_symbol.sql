-- db\sql\stock_data\get_stock_data_by_symbol.sql

-- This SQL query retrieves the most recent stock data for a specific symbol from the stock_data table.
SELECT * FROM stock_data
WHERE symbol = %s
ORDER BY timestamp DESC