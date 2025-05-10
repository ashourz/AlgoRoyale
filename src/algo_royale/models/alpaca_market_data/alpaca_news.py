# src/models/alpaca_models/alpaca_quote.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dateutil.parser import isoparse  # if not using built-in parsing

class NewsImage(BaseModel):
    size: str
    url: str
    
    @staticmethod
    def from_raw(data: dict) -> "NewsImage":
        """
        Convert raw data from Alpaca API response into a NewsImage object.

        Args:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            NewsImage: A NewsImage object populated with values from the raw data.
        
        Example:
            data = {
                "size": "large",
                "url": "https://example.com/image.jpg"
            }
            news_image = NewsImage.from_raw(data)
        """
        return NewsImage(
            size=data["size"],
            url=data["url"]
        )
        
class News(BaseModel):
    """
    Represents a news article related to a stock symbol.
    
    Attributes:
        id (str): Unique identifier for the news article.
        author (str): Author of the news article.
        content (str): Content of the news article.
        created_at (datetime): Timestamp when the news article was created.
        headline (str): Headline of the news article.
        images (List[NewsImage]): List of images associated with the news article.
        source (str): Source of the news article.
        summary (str): Summary of the news article.
        symbols (List[str]): List of stock symbols related to the news article.
        updated_at (datetime): Timestamp when the news article was last updated.
        url (str): URL to the full news article.
        
    Methods:
        from_raw(data: dict) -> News:
            Converts raw dictionary data (from Alpaca API) into a News instance.
            
    Example:
        response = {
            "id": "12345",
            "author": "John Doe",
            "content": "This is a sample news article.",
            "created_at": "2024-04-01T00:00:00Z",
            "headline": "Sample Headline",
            "images": [{"size": "large", "url": "https://example.com/image.jpg"}],
            "source": "News Source",
            "summary": "This is a summary of the news article.",
            "symbols": ["AAPL", "GOOGL"],
            "updated_at": "2024-04-01T01:00:00Z",
            "url": "https://example.com/news/12345"
        }
    """
    
    id: int
    author: str
    content: str
    created_at: datetime
    headline: str
    images: List[NewsImage]
    source: str
    summary: str
    symbols: List[str]  
    updated_at: datetime
    url: str


    @staticmethod
    def from_raw(data: dict) -> "News":
        """
        Convert raw data from Alpaca API response into a News object.
        
        Args:
            data (dict): The raw data returned from Alpaca API.
            
        Returns:
            News: A News object populated with values from the raw data.
            
        Example:
            data = {
                "id": "12345",
                "author": "John Doe",
                "content": "This is a sample news article.",
                "created_at": "2024-04-01T00:00:00Z",
                "headline": "Sample Headline",
                "images": [{"size": "large", "url": "https://example.com/image.jpg"}],
                "source": "News Source",
                "summary": "This is a summary of the news article.",
                "symbols": ["AAPL", "GOOGL"],
                "updated_at": "2024-04-01T01:00:00Z",
                "url": "https://example.com/news/12345"
            }
            news = News.from_raw(data)
        """
        return News(
            id=data["id"],
            author=data["author"],
            content=data["content"],
            created_at=isoparse(data["created_at"]),
            headline=data["headline"],
            images=[NewsImage.from_raw(img) for img in data.get("images", [])],
            source=data["source"],
            summary=data["summary"],
            symbols=data["symbols"],
            updated_at=isoparse(data["updated_at"]),
            url=data["url"]
        )

class NewsResponse(BaseModel):
    """
    Represents the response from the Alpaca API when fetching news data.
    
    Attributes:
        news (List[News]): A list of news articles related to the requested symbols.
    
    Example:
        news_response = NewsResponse(news=[news_article_1, news_article_2])
        where news_article_1 and news_article_2 are instances of the News class.
    """
    
    news: List[News]
    next_page_token: Optional[str]  # Token for pagination if more data is available

    @classmethod
    def from_raw(cls, data: dict) -> Optional["NewsResponse"]:
        """
        Convert raw data from Alpaca API response into a NewsResponse object.
        
        Args:
            data (dict): The raw data returned from Alpaca API.
            
        Returns:
            NewsResponse: A NewsResponse object populated with values from the raw data.
            
        Example:
            response = {
                "news": [
                    {"id": "1", "author": "Author 1", ...},
                    {"id": "2", "author": "Author 2", ...}
                ]
                "next_page_token": "abcd1234"
            }
            news_response = NewsResponse.from_raw(response)
        
        """
        
        if not data or "news" not in data:
            return None

        return cls(
            news=[News.from_raw(n) for n in data["news"]],
            next_page_token=data.get("next_page_token")
        )