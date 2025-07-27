SELECT *
FROM position_trades
WHERE position_id = $1;
-- This SQL statement retrieves all position trades associated with a specific position ID from the position_trades table.