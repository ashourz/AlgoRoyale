
INSERT INTO trade_signals (symbol, signal, price, created_at, user_id, account_id)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (symbol) DO UPDATE
SET signal = EXCLUDED.signal,
    price = EXCLUDED.price,
    created_at = EXCLUDED.created_at,
    user_id = EXCLUDED.user_id,
    account_id = EXCLUDED.account_id
RETURNING id;
-- This SQL statement inserts a new trade signal into the trade_signals table.
-- If a conflict occurs (i.e., a signal for the same symbol already exists), the existing record is updated.