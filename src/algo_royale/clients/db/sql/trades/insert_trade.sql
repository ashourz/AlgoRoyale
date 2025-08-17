
INSERT INTO trades (symbol, market, action, settlement_date, price, quantity, executed_at, created_at, order_id, updated_at, user_id, account_id)
VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_TIMESTAMP, $8, CURRENT_TIMESTAMP, $9, $10)
RETURNING id;
-- This SQL statement inserts a new trade into the trades table with the provided values.
-- The trade's ID is returned after insertion.