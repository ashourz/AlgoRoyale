UPDATE trades SET settled = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING id;
-- This SQL statement updates the 'settled' status of a trade in the trades table based