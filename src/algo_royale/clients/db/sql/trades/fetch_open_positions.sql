SELECT *
FROM (
    SELECT
        symbol,
        market,
        user_id,
        account_id,
        SUM(
            CASE
                WHEN action = 'buy' THEN quantity
                WHEN action = 'sell' THEN -quantity
                ELSE 0
            END
        ) AS net_position
    FROM trades
    WHERE user_id = %s
    AND account_id = %s
    GROUP BY symbol, market, account_id
) positions
WHERE net_position <> 0;
-- Fetch open positions for a specific user and account