DELETE FROM orders
WHERE id = %s RETURNING id;
-- This SQL statement deletes an order from the orders table based on the provided order ID.