SELECT * FROM positions WHERE symbol = $1 AND user_id = $2 AND account_id = $3;
-- This SQL statement retrieves all positions for a specific symbol from the positions table.