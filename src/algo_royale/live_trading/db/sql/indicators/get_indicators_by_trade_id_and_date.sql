-- db\sql\indicators\get_indicators_by_trade_id_and_date.sql

SELECT * FROM indicators
WHERE trade_id = %s
AND recorded_at BETWEEN %s AND %s
ORDER BY recorded_at DESC;
