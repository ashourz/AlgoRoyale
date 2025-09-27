
INSERT INTO trades (symbol, action, settlement_date, price, quantity, executed_at, created_at, order_id, updated_at, user_id, account_id)
VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, CURRENT_TIMESTAMP, %s, %s)
RETURNING id;
-- This SQL statement inserts a new trade into the trades table with the provided values.
-- The trade's ID is returned after insertion.