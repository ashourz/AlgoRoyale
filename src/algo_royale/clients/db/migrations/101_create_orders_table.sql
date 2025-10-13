-- Orders table
CREATE TABLE
    orders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        symbol TEXT NOT NULL,
        order_type TEXT NOT NULL,
        status TEXT NOT NULL,
        action TEXT NOT NULL,
        settled BOOLEAN DEFAULT FALSE,
        notional NUMERIC(20, 10),
        quantity NUMERIC(20, 10),
        price NUMERIC(20, 10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id TEXT,
        account_id TEXT
    );