SELECT pid, usename, state, query, wait_event_type, wait_event, backend_start
FROM pg_stat_activity
WHERE state != 'idle';