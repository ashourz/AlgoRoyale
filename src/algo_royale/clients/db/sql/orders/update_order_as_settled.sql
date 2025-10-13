UPDATE orders SET settled = TRUE WHERE id = :order_id RETURNING id;
-- Update the order status to settled, indicating that the order has been fully processed and no further action is required.