-- db\sql\trades\get_open_trades.sql

SELECT * FROM trades WHERE status = 'open' ORDER BY entry_time DESC LIMIT %s OFFSET %s;