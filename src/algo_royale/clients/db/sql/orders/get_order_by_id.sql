SELECT * FROM orders WHERE id = $1 AND user_id = $2 AND account_id = $3;
-- This query retrieves an order by its ID, ensuring that it belongs to the specified user and