-- db\sql\stock_data\insert_stock_data.sql

-- This SQL script inserts stock data into the stock_data table.
INSERT INTO stock_data (symbol, timestamp, open, high, low, close, volume)
VALUES (%s, %s, %s, %s, %s, %s, %s)