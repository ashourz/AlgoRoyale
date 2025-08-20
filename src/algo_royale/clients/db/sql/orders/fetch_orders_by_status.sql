SELECT *
FROM orders
WHERE status IN $(1)
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;