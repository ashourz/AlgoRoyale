-- db\sql\trades\insert_trade.sql
--
-- This SQL script inserts a new trade into the trades table.
INSERT INTO trades (symbol, price, trade_time)
VALUES (%s, %s, %s)