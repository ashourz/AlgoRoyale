UPDATE current_price = $1, unrealized_pnl = $2, updated_at = CURRENT_TIMESTAMP
 WHERE id = $3
 RETURNING *;