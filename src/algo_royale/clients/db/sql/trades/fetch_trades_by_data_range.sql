SELECT * FROM trades
WHERE trade_date >= %s AND trade_date <= %s
ORDER BY trade_date
LIMIT %s OFFSET %s;
