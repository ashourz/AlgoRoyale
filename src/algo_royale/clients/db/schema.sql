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
        settled BOOLEAN DEFAULT FALSE,
        notional NUMERIC(20, 10),
        quantity INTEGER,
        price NUMERIC(20, 10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id TEXT,
        account_id TEXT
    );

-- Trades table
CREATE TABLE
    trades (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        external_id TEXT UNIQUE,  -- ID from external source
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        settled BOOLEAN DEFAULT FALSE,
        settlement_date TIMESTAMP,
        price NUMERIC(20, 10),
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
        open_price NUMERIC(20, 10),
        high_price NUMERIC(20, 10),
        low_price NUMERIC(20, 10),
        close_price NUMERIC(20, 10),
        num_trades INTEGER,
        volume_weighted_price NUMERIC(20, 10),
        pct_return NUMERIC(20, 10),
        log_return NUMERIC(20, 10),
        sma_10 NUMERIC(20, 10),
        sma_20 NUMERIC(20, 10),
        sma_50 NUMERIC(20, 10),
        sma_100 NUMERIC(20, 10),
        sma_150 NUMERIC(20, 10),
        sma_200 NUMERIC(20, 10),
        macd NUMERIC(20, 10),
        macd_signal NUMERIC(20, 10),
        rsi NUMERIC(20, 10),
        ema_9 NUMERIC(20, 10),
        ema_10 NUMERIC(20, 10),
        ema_12 NUMERIC(20, 10),
        ema_20 NUMERIC(20, 10),
        ema_26 NUMERIC(20, 10),
        ema_50 NUMERIC(20, 10),
        ema_100 NUMERIC(20, 10),
        ema_150 NUMERIC(20, 10),
        ema_200 NUMERIC(20, 10),
        volatility_10 NUMERIC(20, 10),
        volatility_20 NUMERIC(20, 10),
        volatility_50 NUMERIC(20, 10),
        atr_14 NUMERIC(20, 10),
        hist_volatility_20 NUMERIC(20, 10),
        range NUMERIC(20, 10),
        body NUMERIC(20, 10),
        upper_wick NUMERIC(20, 10),
        lower_wick NUMERIC(20, 10),
        vol_ma_10 NUMERIC(20, 10),
        vol_ma_20 NUMERIC(20, 10),
        vol_ma_50 NUMERIC(20, 10),
        vol_ma_100 NUMERIC(20, 10),
        vol_ma_200 NUMERIC(20, 10),
        vol_change NUMERIC(20, 10),
        vwap_10 NUMERIC(20, 10),
        vwap_20 NUMERIC(20, 10),
        vwap_50 NUMERIC(20, 10),
        vwap_100 NUMERIC(20, 10),
        vwap_150 NUMERIC(20, 10),
        vwap_200 NUMERIC(20, 10),
        hour NUMERIC(20, 10),
        day_of_week NUMERIC(20, 10),
        adx NUMERIC(20, 10),
        momentum_10 NUMERIC(20, 10),
        roc_10 NUMERIC(20, 10),
        stochastic_k NUMERIC(20, 10),
        stochastic_d NUMERIC(20, 10),
        bollinger_upper NUMERIC(20, 10),
        bollinger_lower NUMERIC(20, 10),
        bollinger_width NUMERIC(20, 10),
        gap NUMERIC(20, 10),
        high_low_ratio NUMERIC(20, 10),
        obv NUMERIC(20, 10),
        adl NUMERIC(20, 10)
    );

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


-- Indexes for performance
CREATE INDEX idx_trade_symbol ON trades (symbol);
CREATE INDEX idx_orders_user_account ON orders (user_id, account_id);
