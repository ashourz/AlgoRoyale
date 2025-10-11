INSERT INTO data_stream_session (stream_class, symbol, application_env, start_time) VALUES (%s, %s, %s, %s) RETURNING id;
