SELECT * FROM trades
WHERE trade_date >= $1 AND trade_date <= $2
ORDER BY trade_date
LIMIT $3 OFFSET $4;
