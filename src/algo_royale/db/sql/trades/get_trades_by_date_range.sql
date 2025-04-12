-- db\sql\trades\get_trades_by_date_range.sql

SELECT * FROM trades WHERE entry_time BETWEEN %s AND %s ORDER BY entry_time DESC LIMIT %s OFFSET %s;



