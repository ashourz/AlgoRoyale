-- migrations/001_initial_setup.sql

DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS trade_signals;
DROP TABLE IF EXISTS indicators;
DROP TABLE IF EXISTS news_sentiment;    
DROP TABLE IF EXISTS stock_data;

-- Create schema migrations table
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
