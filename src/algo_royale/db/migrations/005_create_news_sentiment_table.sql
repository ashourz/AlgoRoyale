-- migrations/003_create_dependent_tables.sql

-- News Sentiment table
CREATE TABLE
    news_sentiment (
        id SERIAL PRIMARY KEY,
        trade_id INTEGER REFERENCES trades (id) ON DELETE CASCADE,
        symbol TEXT,
        sentiment_score NUMERIC(4, 2),
        headline TEXT,
        source TEXT,
        published_at TIMESTAMP
    );