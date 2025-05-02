-- db\migrations\006_create_stock_data_table.sql

-- Create Stock Data table
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    timestamp TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT
);