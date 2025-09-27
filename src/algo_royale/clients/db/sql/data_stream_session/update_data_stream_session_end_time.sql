UPDATE data_stream_session
SET
    end_time = %s
WHERE id = %s
RETURNING id;
