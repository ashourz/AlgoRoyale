SELECT * FROM orders
WHERE status = ANY(%s) AND symbol = %s
ORDER BY created_at DESC
LIMIT %s OFFSET %s;
-- This query retrieves all orders for a specific symbol and status, ordered by creation time in descending