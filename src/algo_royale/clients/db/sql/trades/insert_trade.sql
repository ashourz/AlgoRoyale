
INSERT INTO trades (symbol, market, order_type, action, entry_price, exit_price, shares, entry_time, exit_time, realized_pnl, notes, created_at, order_id, user_id, account_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s)
RETURNING id;
-- This SQL statement inserts a new trade into the trades table with the specified values and returns the ID of the newly created trade.
