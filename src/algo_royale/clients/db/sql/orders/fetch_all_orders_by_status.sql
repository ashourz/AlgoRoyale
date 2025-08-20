SELECT * FROM orders WHERE status IN $(1);
-- Fetch all orders by status