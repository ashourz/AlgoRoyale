UPDATE orders
SET status = %s, 
    quantity = %s, 
    price = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE id = %s
RETURNING id;
-- This SQL statement updates the status and updated_at timestamp of an order in the orders table.