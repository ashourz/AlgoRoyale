
DELETE FROM trades WHERE id = %s RETURNING id;
-- This SQL statement deletes a trade from the trades table based on the provided trade ID and returns
