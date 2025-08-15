SELECT *
FROM position_trades
WHERE position_id = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;
-- This SQL statement retrieves all position trades associated with a specific position ID from the position_trades table.