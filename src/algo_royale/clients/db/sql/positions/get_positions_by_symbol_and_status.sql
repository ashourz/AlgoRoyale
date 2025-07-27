SELECT * FROM positions WHERE symbol = $1 AND status = $2
ORDER BY created_at DESC LIMIT $3 OFFSET $4;
-- This SQL statement retrieves all positions for a specific symbol and status from the positions table.