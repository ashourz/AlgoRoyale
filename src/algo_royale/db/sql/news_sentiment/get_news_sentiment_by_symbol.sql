-- db\sql\news_sentiment\get_news_sentiment_by_symbol.sql
 
SELECT * FROM news_sentiment
WHERE symbol = %s
ORDER BY published_at DESC