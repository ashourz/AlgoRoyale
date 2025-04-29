-- db\sql\trades\get_all_trades.sql

SELECT * FROM trades ORDER BY entry_time DESC LIMIT %s OFFSET %s;
