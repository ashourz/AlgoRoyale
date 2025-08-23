-- db\schema.sql
-- This file defines the schema for the Algo Royale database
-- It includes the creation of tables, indexes, and other database objects
-- This file is for reference only and should not be executed directly

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS enriched_data;
DROP TABLE IF EXISTS data_stream_session;

-- DB Migrations
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE
    orders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        symbol TEXT NOT NULL,
        order_type TEXT NOT NULL,
        status TEXT NOT NULL,
        action TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price NUMERIC(10, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id TEXT,
        account_id TEXT
    );

-- Trades table
CREATE TABLE
    trades (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        settled BOOLEAN DEFAULT FALSE,
        settlement_date TIMESTAMP,
        price NUMERIC(10, 4),
        quantity INTEGER,
        executed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        order_id UUID REFERENCES orders (id) ON DELETE CASCADE,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id TEXT,
        account_id TEXT
    );

-- Enriched Data table
CREATE TABLE
    enriched_data (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        order_id UUID REFERENCES orders (id) ON DELETE CASCADE,
        market_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        symbol TEXT NOT NULL,
        market TEXT NOT NULL,
        volume NUMERIC(12, 2),
        open_price NUMERIC(10, 4),
        high_price NUMERIC(10, 4),
        low_price NUMERIC(10, 4),
        close_price NUMERIC(10, 4),
        num_trades INTEGER,
        volume_weighted_price NUMERIC(10, 4),
        pct_return NUMERIC(10, 4),
        log_return NUMERIC(10, 4),
        sma_10 NUMERIC(10, 4),
        sma_20 NUMERIC(10, 4),
        sma_50 NUMERIC(10, 4),
        sma_100 NUMERIC(10, 4),
        sma_150 NUMERIC(10, 4),
        sma_200 NUMERIC(10, 4),
        macd NUMERIC(10, 4),
        macd_signal NUMERIC(10, 4),
        rsi NUMERIC(10, 4),
        ema_9 NUMERIC(10, 4),
        ema_10 NUMERIC(10, 4),
        ema_12 NUMERIC(10, 4),
        ema_20 NUMERIC(10, 4),
        ema_26 NUMERIC(10, 4),
        ema_50 NUMERIC(10, 4),
        ema_100 NUMERIC(10, 4),
        ema_150 NUMERIC(10, 4),
        ema_200 NUMERIC(10, 4),
        volatility_10 NUMERIC(10, 4),
        volatility_20 NUMERIC(10, 4),
        volatility_50 NUMERIC(10, 4),
        atr_14 NUMERIC(10, 4),
        hist_volatility_20 NUMERIC(10, 4),
        range NUMERIC(10, 4),
        body NUMERIC(10, 4),
        upper_wick NUMERIC(10, 4),
        lower_wick NUMERIC(10, 4),
        vol_ma_10 NUMERIC(10, 4),
        vol_ma_20 NUMERIC(10, 4),
        vol_ma_50 NUMERIC(10, 4),
        vol_ma_100 NUMERIC(10, 4),
        vol_ma_200 NUMERIC(10, 4),
        vol_change NUMERIC(10, 4),
        vwap_10 NUMERIC(10, 4),
        vwap_20 NUMERIC(10, 4),
        vwap_50 NUMERIC(10, 4),
        vwap_100 NUMERIC(10, 4),
        vwap_150 NUMERIC(10, 4),
        vwap_200 NUMERIC(10, 4),
        hour NUMERIC(10, 4),
        day_of_week NUMERIC(10, 4),
        adx NUMERIC(10, 4),
        momentum_10 NUMERIC(10, 4),
        roc_10 NUMERIC(10, 4),
        stochastic_k NUMERIC(10, 4),
        stochastic_d NUMERIC(10, 4),
        bollinger_upper NUMERIC(10, 4),
        bollinger_lower NUMERIC(10, 4),
        bollinger_width NUMERIC(10, 4),
        gap NUMERIC(10, 4),
        high_low_ratio NUMERIC(10, 4),
        obv NUMERIC(10, 4)
        adl NUMERIC(10, 4),
    );

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


-- Indexes for performance
CREATE INDEX idx_trade_symbol ON trades (symbol);
CREATE INDEX idx_orders_user_account ON orders (user_id, account_id);
