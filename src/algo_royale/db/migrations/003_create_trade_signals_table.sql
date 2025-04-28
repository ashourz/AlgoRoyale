-- db\migrations\003_create_trade_signals_table.sql

-- Trade Signals table
CREATE TABLE
    trade_signals (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        signal TEXT NOT NULL, -- BUY, SELL, HOLD, etc.
        price NUMERIC NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );