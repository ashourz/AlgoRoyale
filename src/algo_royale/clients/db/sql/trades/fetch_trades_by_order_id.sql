SELECT id, user_id, account_id, symbol, action, settled, settlement_date, price, quantity, executed_at, created_at, order_id, updated_at
FROM trades
WHERE order_id = %s;
-- Fetch trades by order ID