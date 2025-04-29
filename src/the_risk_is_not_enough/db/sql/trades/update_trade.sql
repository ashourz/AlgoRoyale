
UPDATE trades
SET symbol = %s, direction = %s, entry_price = %s, exit_price = %s, shares = %s, entry_time = %s, exit_time = %s, strategy_phase = %s, pnl = %s, notes = %s
WHERE id = %s;
