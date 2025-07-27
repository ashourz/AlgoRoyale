
INSERT INTO trades (symbol, market, action, price, shares, executed_at, notes, created_at, order_id, user_id, account_id)
VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, $6, CURRENT_TIMESTAMP, $7, $8, $9)
RETURNING id;
-- This SQL statement inserts a new trade into the trades table with the provided values.
-- The trade's ID is returned after insertion.