INSERT INTO positions (symbol, quantity, entry_price, current_price, pnl, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, NOW(), NOW());