
UPDATE news_sentiment
SET sentiment_score = %s, headline = %s, source = %s, published_at = %s
WHERE id = %s;
