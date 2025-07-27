
-- Positions table
CREATE TABLE
    positions (
        id SERIAL PRIMARY KEY,  -- Unique identifier for the position
        symbol TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        entry_price NUMERIC(10, 4),
        current_price NUMERIC(10, 4),
        unrealized_pnl NUMERIC(10, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        -- Assuming user_id and account_id are used for tracking positions per user/account
        user_id UUID,
        account_id TEXT
    );