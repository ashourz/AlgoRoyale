-- db\sql\stock_data\get_stock_data_by_symbol_and_timestamp copy.sql
SELECT * FROM stock_data WHERE symbol = %s AND timestamp BETWEEN %s AND %s ORDER BY timestamp ASC;