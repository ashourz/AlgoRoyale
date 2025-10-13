SELECT id, user_id, account_id, symbol, action, settled, settlement_date, price, quantity, executed_at, created_at, order_id, updated_at FROM trades
WHERE executed_at >= %s AND executed_at <= %s
ORDER BY executed_at
LIMIT %s OFFSET %s;
