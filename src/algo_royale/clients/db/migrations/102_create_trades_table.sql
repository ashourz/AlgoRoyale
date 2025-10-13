-- db\migrations\102_create_trades_table.sql

-- Trades table
CREATE TABLE
    trades (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        external_id TEXT UNIQUE,  -- ID from external source
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        settled BOOLEAN DEFAULT FALSE,
        settlement_date TIMESTAMP,
        price NUMERIC(20, 10),
        quantity NUMERIC(20, 10),
        executed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        order_id UUID REFERENCES orders (id) ON DELETE CASCADE,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id TEXT,
        account_id TEXT
    );