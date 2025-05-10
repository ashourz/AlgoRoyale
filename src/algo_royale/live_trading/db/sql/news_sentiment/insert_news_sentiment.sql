-- db\sql\news_sentiment\insert_news_sentiment.sql

-- This SQL script inserts news sentiment data into the news_sentiment table.
INSERT INTO news_sentiment (trade_id, symbol, sentiment_score, headline, source, published_at)
VALUES (%s, %s, %s, %s, %s, %s) 
