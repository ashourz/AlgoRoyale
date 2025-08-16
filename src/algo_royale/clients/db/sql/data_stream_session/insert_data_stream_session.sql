INSERT INTO data_stream_session (
    stream_type,
    symbol,
    strategy_name,
    start_time,
) VALUES (
    $1, $2, $3, $4, $5
) RETURNING id;
