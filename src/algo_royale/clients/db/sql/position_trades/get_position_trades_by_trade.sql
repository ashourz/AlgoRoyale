SELECT *
FROM position_trades
WHERE trade_id = $1;
-- This SQL statement retrieves all position trades associated with a specific trade ID from the position_trades table.