-- db\sql\indicators\get_indicators_by_trade_id.sql

-- This SQL query retrieves all indicators associated with a specific trade ID from the indicators table.
-- It orders the results by the recorded_at timestamp in descending order.
SELECT * FROM indicators
Where trade_id = %s
ORDER BY recorded_at DESC