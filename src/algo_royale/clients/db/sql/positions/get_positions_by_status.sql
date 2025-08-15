SELECT * FROM positions WHERE status = $1 AND user_id = $2 AND account_id = $3 LIMIT $4 OFFSET $5;
-- Fetch positions by their status for a specific user and account.
