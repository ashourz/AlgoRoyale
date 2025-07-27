-- db\schema.sql
DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS trade_signals;
DROP TABLE IF EXISTS indicators;
DROP TABLE IF EXISTS news_sentiment;    
DROP TABLE IF EXISTS stock_data;

-- DB Migrations
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trade Signals table
CREATE TABLE
    trade_signals (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        signal TEXT NOT NULL, -- BUY, SELL, HOLD, etc.
        price NUMERIC NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id UUID,
        account_id TEXT
    );

-- Orders table
CREATE TABLE
    orders (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        market TEXT NOT NULL,
        order_type TEXT CHECK (order_type IN ('market', 'limit', 'stop')) NOT NULL,
        status TEXT CHECK (status IN ('pending', 'partially_filled', 'filled', 'cancelled')) NOT NULL,
        action TEXT CHECK (action IN ('buy', 'sell')) NOT NULL,
        quantity INTEGER NOT NULL,
        price NUMERIC(10, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        signal_id INTEGER REFERENCES trade_signals (id) ON DELETE CASCADE,
        user_id UUID,
        account_id TEXT
    );
CREATE INDEX idx_orders_user_account ON orders (user_id, account_id);

-- Trades table
CREATE TABLE
    trades (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        market TEXT NOT NULL,
        order_type TEXT CHECK (order_type IN ('market', 'limit', 'stop')) NOT NULL,
        action TEXT CHECK (action IN ('buy', 'sell')) NOT NULL,
        settled BOOLEAN DEFAULT FALSE,
        settlement_date TIMESTAMP,
        entry_price NUMERIC(10, 4),
        exit_price NUMERIC(10, 4),
        shares INTEGER,
        entry_time TIMESTAMP,
        exit_time TIMESTAMP,
        realized_pnl NUMERIC(10, 4),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        order_id INTEGER REFERENCES orders (id) ON DELETE CASCADE,
        user_id UUID,
        account_id TEXT
    );

-- Positions table
CREATE TABLE
    positions (
        id SERIAL PRIMARY KEY,  -- Unique identifier for the position
        symbol TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        entry_price NUMERIC(10, 4),
        current_price NUMERIC(10, 4),
        unrealized_pnl NUMERIC(10, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        -- Assuming user_id and account_id are used for tracking positions per user/account
        user_id UUID,
        account_id TEXT
    );

CREATE INDEX idx_positions_user_account ON positions (user_id, account_id)

-- Position Trades table
CREATE TABLE
    position_trades (
        id SERIAL PRIMARY KEY,
        position_id INTEGER REFERENCES positions (id) ON DELETE CASCADE,
        trade_id INTEGER REFERENCES trades (id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE UNIQUE INDEX idx_position_trades_unique ON position_trades(position_id, trade_id);

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
    );

-- Indexes for performance
CREATE INDEX idx_trade_symbol ON trades (symbol);
CREATE INDEX idx_trade_signals_symbol ON trade_signals (symbol);
CREATE INDEX idx_indicators_trade_id ON indicators (trade_id);
CREATE INDEX idx_news_sentiment_trade_id ON news_sentiment (trade_id);
CREATE INDEX idx_news_sentiment_symbol ON news_sentiment (symbol);
CREATE INDEX idx_stock_data_symbol ON stock_data (symbol);
