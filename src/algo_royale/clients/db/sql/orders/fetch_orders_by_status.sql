SELECT *
FROM orders
WHERE status = ANY(%s)
ORDER BY created_at DESC
LIMIT %s OFFSET %s;