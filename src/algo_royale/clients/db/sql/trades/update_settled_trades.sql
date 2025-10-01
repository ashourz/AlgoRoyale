UPDATE trades
SET settled = TRUE
WHERE settled = FALSE AND settlement_date <= %s
RETURNING id;