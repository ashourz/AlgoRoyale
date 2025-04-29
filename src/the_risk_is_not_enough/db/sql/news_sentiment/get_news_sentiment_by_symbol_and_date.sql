-- db\sql\news_sentiment\get_news_sentiment_by_symbol_and_date.sql
 
SELECT * FROM news_sentiment WHERE symbol = %s AND published_at BETWEEN %s AND %s
ORDER BY published_at DESC;