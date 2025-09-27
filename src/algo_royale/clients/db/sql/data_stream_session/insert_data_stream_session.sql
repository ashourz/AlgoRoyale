INSERT INTO data_stream_session (stream_type, symbol, strategy_name, start_time) VALUES (%s, %s, %s, %s) RETURNING id;
