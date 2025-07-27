UPDATE orders
SET status = $1, 
    updated_at = CURRENT_TIMESTAMP
WHERE id = $2
RETURNING id;
-- This SQL statement updates the status and updated_at timestamp of an order in the orders table.