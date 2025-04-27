-- migrations/003_create_dependent_tables.sql

-- Indicators table
CREATE TABLE
    indicators (
        id SERIAL PRIMARY KEY,
        trade_id INTEGER REFERENCES trades (id) ON DELETE CASCADE,
        rsi NUMERIC(5, 2),
        macd NUMERIC(10, 4),
        macd_signal NUMERIC(10, 4),
        volume NUMERIC(12, 2),
        bollinger_upper NUMERIC(10, 4),
        bollinger_lower NUMERIC(10, 4),
        atr NUMERIC(10, 4),
        price NUMERIC(10, 4),
        ema_short NUMERIC(10, 4),
        ema_long NUMERIC(10, 4),
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );