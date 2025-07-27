INSERT INTO positions (symbol, quantity, price, created_at, updated_at, user_id, account_id)
VALUES ($1, $2, $3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, $4, $5)
ON CONFLICT (symbol, user_id, account_id)
DO UPDATE SET
  quantity = positions.quantity + EXCLUDED.quantity,
  price = EXCLUDED.price,
  updated_at = CURRENT_TIMESTAMP
RETURNING id;
-- This SQL statement inserts a new position into the positions table with the provided values.