-- db\migrations\002_create_trades_table.sql

-- Data Stream Session table
CREATE TABLE
    data_stream_session (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        stream_type TEXT NOT NULL, -- e.g., 'portfolio', 'symbol', etc.
        symbol TEXT NOT NULL,
        strategy_name TEXT,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP DEFAULT NULL
    );