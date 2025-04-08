-- db\sql\trade_signals\insert_signal.sql

-- This SQL script inserts a new trade signal into the trade_signals table.
INSERT INTO trade_signals (symbol, signal, price, created_at)
VALUES (%s, %s, %s, NOW())