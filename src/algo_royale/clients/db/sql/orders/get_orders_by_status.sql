SELECT *
FROM orders
WHERE status = $1
ORDER BY created_at DESC;