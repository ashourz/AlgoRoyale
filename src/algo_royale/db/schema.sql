-- db\schema.sql
DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS trade_signals;
DROP TABLE IF EXISTS indicators;
DROP TABLE IF EXISTS news_sentiment;    
DROP TABLE IF EXISTS stock_data;

-- Trades table
CREATE TABLE
    trades (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        direction TEXT CHECK (direction IN ('long', 'short')) NOT NULL,
        entry_price NUMERIC(10, 4),
        exit_price NUMERIC(10, 4),
        shares INTEGER,
        entry_time TIMESTAMP,
        exit_time TIMESTAMP,
        strategy_phase TEXT CHECK (
            strategy_phase IN ('breakout', 'momentum', 'mean_reversion')
        ),
        pnl NUMERIC(10, 4),
        notes TEXT
    );

-- Trade Signals table
CREATE TABLE
    trade_signals (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        signal TEXT NOT NULL, -- BUY, SELL, HOLD, etc.
        price NUMERIC NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Indicators table
CREATE TABLE
    indicators (
        id SERIAL PRIMARY KEY,
        trade_id INTEGER REFERENCES trades (id) ON DELETE CASCADE,
        rsi NUMERIC(5, 2),
        macd NUMERIC(10, 4),
        macd_signal NUMERIC(10, 4),
        volume NUMERIC(12, 2),
        bollinger_upper NUMERIC(10, 4),
        bollinger_lower NUMERIC(10, 4),
        atr NUMERIC(10, 4),
        price NUMERIC(10, 4),
        ema_short NUMERIC(10, 4),
        ema_long NUMERIC(10, 4),
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

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

-- Stock Date table
CREATE TABLE
    stock_data (
        id SERIAL PRIMARY KEY,
        symbol TEXT,
        timestamp TIMESTAMP,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume INT
    )   close FLOAT,
        volume INT
    )