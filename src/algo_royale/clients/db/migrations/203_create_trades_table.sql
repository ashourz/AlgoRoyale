-- db\migrations\002_create_trades_table.sql

-- Trades table
CREATE TABLE
    trades (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        market TEXT NOT NULL,
        action TEXT CHECK (action IN ('buy', 'sell')) NOT NULL,
        settled BOOLEAN DEFAULT FALSE,
        settlement_date TIMESTAMP,
        price NUMERIC(10, 4),
        shares INTEGER,
        executed_at TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        order_id INTEGER REFERENCES orders (id) ON DELETE CASCADE,
        user_id UUID,
        account_id TEXT
    );