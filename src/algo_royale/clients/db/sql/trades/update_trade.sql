UPDATE trades SET settled = TRUE WHERE id = %s RETURNING id;
-- This SQL statement updates the 'settled' status of a trade in the trades table based