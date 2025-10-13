INSERT INTO orders (symbol, order_type, status, action, notional, quantity, price, created_at, updated_at, user_id, account_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s, %s)
RETURNING id; 
-- This SQL statement inserts a new order into the orders table with the provided parameters and returns the newly created order's ID.