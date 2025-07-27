INSERT INTO orders (symbol, order_type, status, direction, quantity, filled_quantity, price, created_at, signal_id, user_id, account_id)
VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_TIMESTAMP, $8, $9, $10)
RETURNING order_id; 
-- This SQL statement inserts a new order into the orders table with the provided parameters and returns the newly created order's ID.