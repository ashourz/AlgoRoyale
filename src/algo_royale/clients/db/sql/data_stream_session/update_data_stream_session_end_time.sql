UPDATE data_stream_session
SET
    end_time = $5
WHERE id = $6
RETURNING id;
