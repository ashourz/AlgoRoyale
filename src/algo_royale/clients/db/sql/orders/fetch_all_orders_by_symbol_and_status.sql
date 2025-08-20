SELECT * FROM orders
WHERE status IN $(1) AND symbol = $2
ORDER BY created_at DESC;
-- This query retrieves all orders for a specific symbol and status, ordered by creation time in descending 