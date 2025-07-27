INSERT INTO positions (symbol, quantity, entry_price, current_price, unrealized_pnl, created_at, updated_at, user_id, account_id)
VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, $6, $7)
RETURNING id;
-- This SQL statement inserts a new position into the positions table and returns the ID of the newly created position.