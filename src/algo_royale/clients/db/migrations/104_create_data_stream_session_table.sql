-- db\migrations\002_create_trades_table.sql

-- Data Stream Session table
CREATE TABLE
    data_stream_session (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        stream_class TEXT NOT NULL,
        symbol TEXT NOT NULL,
        application_env TEXT NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP DEFAULT NULL
    );