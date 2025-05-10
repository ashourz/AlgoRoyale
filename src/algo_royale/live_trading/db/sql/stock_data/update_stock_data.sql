
UPDATE stock_data
SET symbol = %s, timestamp = %s, open = %s, high = %s, low = %s, close = %s, volume = %s
WHERE id = %s;
