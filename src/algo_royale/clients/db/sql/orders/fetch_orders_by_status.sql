SELECT *
FROM orders
WHERE status IN (%s)
ORDER BY created_at DESC
LIMIT %s OFFSET %s;