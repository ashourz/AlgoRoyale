-- db\sql\stock_data\get_latest_stock_data..sql
SELECT * FROM stock_data WHERE symbol = %s ORDER BY timestamp DESC LIMIT 1;
