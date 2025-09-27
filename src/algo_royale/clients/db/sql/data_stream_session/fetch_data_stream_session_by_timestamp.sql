SELECT * FROM data_stream_session
WHERE start_time >= %s
	AND (end_time <= %s OR end_time IS NULL);