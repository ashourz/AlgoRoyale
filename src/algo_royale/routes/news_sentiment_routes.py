from datetime import datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request

from algo_royale.services.news_sentiment_service import NewsSentimentService


def create_news_sentiment_blueprint(service: NewsSentimentService) -> Blueprint:
    """
    Create a Flask blueprint for news sentiment routes.
    :param service: An instance of NewsSentimentService.
    :return: A Flask blueprint with news sentiment routes.
    """
    news_sentiment_bp = Blueprint("news_sentiment", __name__)

    @news_sentiment_bp.route("/", methods=["POST"])
    def create_news_sentiment():
        data = request.json
        service.create_news_sentiment(
            symbol=data["symbol"],
            sentiment_score=Decimal(data["sentiment_score"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
        return jsonify({"message": "News sentiment created"}), 201

    @news_sentiment_bp.route("/<int:news_sentiment_id>", methods=["GET"])
    def get_news_sentiment_by_id(news_sentiment_id):
        news_sentiment = service.get_news_sentiment_by_id(news_sentiment_id)
        return jsonify(news_sentiment)

    @news_sentiment_bp.route("/<string:symbol>", methods=["GET"])
    def get_news_sentiment_by_symbol(symbol):
        news_sentiments = service.get_news_sentiment_by_symbol(symbol)
        return jsonify(news_sentiments)

    @news_sentiment_bp.route(
        "/<string:symbol>/<string:start_date>/<string:end_date>", methods=["GET"]
    )
    def get_news_sentiment_by_symbol_and_date(symbol, start_date, end_date):
        news_sentiments = service.get_news_sentiment_by_symbol_and_date(
            symbol, start_date, end_date
        )
        return jsonify(news_sentiments)

    @news_sentiment_bp.route("/<int:news_sentiment_id>", methods=["PUT"])
    def update_news_sentiment(news_sentiment_id):
        data = request.json
        service.update_news_sentiment(
            news_sentiment_id=news_sentiment_id,
            sentiment_score=Decimal(data["sentiment_score"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
        return jsonify({"message": "News sentiment updated"})

    @news_sentiment_bp.route("/<int:news_sentiment_id>", methods=["DELETE"])
    def delete_news_sentiment(news_sentiment_id):
        service.delete_news_sentiment(news_sentiment_id)
        return jsonify({"message": "News sentiment deleted"})

    return news_sentiment_bp
