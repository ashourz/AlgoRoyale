-- Orders table
CREATE TABLE
    orders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        symbol TEXT NOT NULL,
        order_type TEXT NOT NULL,
        status TEXT NOT NULL,
        action TEXT NOT NULL,
        notional NUMERIC(10, 4),
        quantity INTEGER,
        price NUMERIC(10, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id TEXT,
        account_id TEXT
    );