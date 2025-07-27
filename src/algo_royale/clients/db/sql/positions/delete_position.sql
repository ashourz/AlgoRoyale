DELETE FROM positions
WHERE id = $1
RETURNING id;
-- This SQL statement deletes a position from the positions table based on the provided position ID.