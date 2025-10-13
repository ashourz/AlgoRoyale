SELECT * FROM orders WHERE id = %s AND user_id = %s AND account_id = %s;
-- This query retrieves an order by its ID, ensuring that it belongs to the specified user and