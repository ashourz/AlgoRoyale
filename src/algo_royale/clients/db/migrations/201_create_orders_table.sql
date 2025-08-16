-- Orders table
CREATE TABLE
    orders (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        market TEXT NOT NULL,
        order_type TEXT CHECK (order_type IN ('market', 'limit', 'stop')) NOT NULL,
        status TEXT CHECK (status IN ('pending', 'partially_filled', 'filled', 'cancelled')) NOT NULL,
        action TEXT CHECK (action IN ('buy', 'sell')) NOT NULL,
        quantity INTEGER NOT NULL,
        price NUMERIC(10, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id UUID,
        account_id TEXT
    );