DELETE FROM orders
WHERE id = $1 RETURNING id;
-- This SQL statement deletes an order from the orders table based on the provided order ID.