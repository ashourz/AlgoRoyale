SELECT *
FROM order_trades
WHERE trade_id = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;
-- This SQL statement retrieves all order trades associated with a specific trade ID from the order_trades table.