-- db\migrations\002_create_trades_table.sql

-- Trades table
CREATE TABLE
    trades (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        market TEXT NOT NULL,
        order_type TEXT CHECK (order_type IN ('market', 'limit', 'stop')) NOT NULL,
        action TEXT CHECK (action IN ('buy', 'sell')) NOT NULL,
        settled BOOLEAN DEFAULT FALSE,
        settlement_date TIMESTAMP,
        entry_price NUMERIC(10, 4),
        exit_price NUMERIC(10, 4),
        shares INTEGER,
        entry_time TIMESTAMP,
        exit_time TIMESTAMP,
        realized_pnl NUMERIC(10, 4),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        order_id INTEGER REFERENCES orders (id) ON DELETE CASCADE,
        user_id UUID,
        account_id TEXT
    );