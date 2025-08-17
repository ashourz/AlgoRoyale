UPDATE trades
SET status = 1
WHERE status = 0 AND settlement_date <= %s
RETURNING id;