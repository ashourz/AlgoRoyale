-- db\migrations\007_create_indexes.sql

-- Indexes for performance
CREATE INDEX idx_trade_symbol ON trades (symbol);
CREATE INDEX idx_trade_signals_symbol ON trade_signals (symbol);
CREATE INDEX idx_indicators_trade_id ON indicators (trade_id);
CREATE INDEX idx_news_sentiment_trade_id ON news_sentiment (trade_id);
CREATE INDEX idx_news_sentiment_symbol ON news_sentiment (symbol);
CREATE INDEX idx_stock_data_symbol ON stock_data (symbol);
