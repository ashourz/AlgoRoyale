-- db\sql\trades\get_unsettled_trades.sql

SELECT * FROM trades WHERE settled = FALSE ORDER BY settlement_date DESC LIMIT %s OFFSET %s;
-- This SQL statement retrieves all unsettled trades from the trades table, ordered by settlement date in descending order,
-- with pagination support using LIMIT and OFFSET.  