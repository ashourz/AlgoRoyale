SELECT *
FROM trades
WHERE order_id = :order_id;
-- Fetch trades by order ID