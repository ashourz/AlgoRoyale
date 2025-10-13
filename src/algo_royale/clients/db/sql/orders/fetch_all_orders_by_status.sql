SELECT * FROM orders WHERE status = ANY(%s);
-- Fetch all orders by status