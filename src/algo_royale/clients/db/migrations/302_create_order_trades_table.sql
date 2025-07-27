-- Order Trades table
CREATE TABLE
    order_trades (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders (id) ON DELETE CASCADE,
        trade_id INTEGER REFERENCES trades (id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );