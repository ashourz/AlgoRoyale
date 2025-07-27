UPDATE positions
SET
  current_price = $2,
  updated_at = CURRENT_TIMESTAMP
WHERE id = $1
RETURNING id;
-- This SQL statement updates the current price of a position based on the provided position ID and returns the ID of the updated position.