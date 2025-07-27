-- Position Trades table
CREATE TABLE
    position_trades (
        id SERIAL PRIMARY KEY,
        position_id INTEGER REFERENCES positions (id) ON DELETE CASCADE,
        trade_id INTEGER REFERENCES trades (id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );