SELECT * FROM positions WHERE status = $1
ORDER BY created_at DESC LIMIT $2 OFFSET $3;
-- This SQL statement retrieves all positions with a specific status from the positions table.