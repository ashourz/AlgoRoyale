UPDATE orders
SET status = $1, 
    quantity = $2, 
    price = $3,
    updated_at = CURRENT_TIMESTAMP
WHERE id = $4
RETURNING id;
-- This SQL statement updates the status and updated_at timestamp of an order in the orders table.