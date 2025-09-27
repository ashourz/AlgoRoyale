SELECT * FROM orders
WHERE status IN (%s) AND symbol = %s
ORDER BY created_at DESC;
-- This query retrieves all orders for a specific symbol and status, ordered by creation time in descending 