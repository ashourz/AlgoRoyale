-- -- db\sql\trades\get_trade_by_id.sql
-- -- This SQL query retrieves a specific trade by its ID from the trades table.
SELECT * FROM trades WHERE id = %s ORDER BY entry_time DESC;



