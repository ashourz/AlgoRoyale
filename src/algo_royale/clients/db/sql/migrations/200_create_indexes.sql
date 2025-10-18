-- db\migrations\007_create_indexes.sql

-- Indexes for performance
CREATE INDEX idx_trade_symbol ON trades (symbol);
CREATE INDEX idx_orders_user_account ON orders (user_id, account_id);
