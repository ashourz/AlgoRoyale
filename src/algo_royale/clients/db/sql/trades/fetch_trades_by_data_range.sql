SELECT id, user_id, account_id, symbol, action, settled, settlement_date, price, quantity, executed_at, created_atorder_id, updated_at FROM trades
WHERE trade_date >= %s AND trade_date <= %s
ORDER BY trade_date
LIMIT %s OFFSET %s;
