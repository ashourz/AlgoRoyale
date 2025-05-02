# src/routes/indicator_routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal
from algo_royale.shared.service.db.indicator_service import IndicatorService

indicator_bp = Blueprint("indicator", __name__)
service = IndicatorService()

@indicator_bp.route("/", methods=["POST"])
def insert_indicator():
    data = request.json
    service.insert_indicator(
        trade_id=data["trade_id"],
        rsi=Decimal(data["rsi"]),
        macd=Decimal(data["macd"]),
        macd_signal=Decimal(data["macd_signal"]),
        volume=Decimal(data["volume"]),
        bollinger_upper=Decimal(data["bollinger_upper"]),
        bollinger_lower=Decimal(data["bollinger_lower"]),
        atr=Decimal(data["atr"]),
        price=Decimal(data["price"]),
        ema_short=Decimal(data["ema_short"]),
        ema_long=Decimal(data["ema_long"]),
        recorded_at=datetime.fromisoformat(data["recorded_at"])
    )
    return jsonify({"message": "Indicator inserted"}), 201

@indicator_bp.route("/<int:trade_id>", methods=["GET"])
def fetch_by_trade_id(trade_id):
    indicators = service.fetch_by_trade_id(trade_id)
    return jsonify(indicators)

@indicator_bp.route("/<int:trade_id>/<string:start_date>/<string:end_date>", methods=["GET"])
def fetch_by_trade_id_and_date(trade_id, start_date, end_date):
    indicators = service.fetch_by_trade_id_and_date(trade_id, start_date, end_date)
    return jsonify(indicators)

@indicator_bp.route("/<int:indicator_id>", methods=["PUT"])
def update_indicator(indicator_id):
    data = request.json
    service.update_indicator(
        indicator_id=indicator_id,
        rsi=Decimal(data["rsi"]),
        macd=Decimal(data["macd"]),
        macd_signal=Decimal(data["macd_signal"]),
        volume=Decimal(data["volume"]),
        bollinger_upper=Decimal(data["bollinger_upper"]),
        bollinger_lower=Decimal(data["bollinger_lower"]),
        atr=Decimal(data["atr"]),
        price=Decimal(data["price"]),
        ema_short=Decimal(data["ema_short"]),
        ema_long=Decimal(data["ema_long"]),
        recorded_at=datetime.fromisoformat(data["recorded_at"])
    )
    return jsonify({"message": "Indicator updated"}), 200

@indicator_bp.route("/<int:indicator_id>", methods=["DELETE"])
def delete_indicator(indicator_id):
    service.delete_indicator(indicator_id)
    return jsonify({"message": "Indicator deleted"}), 200
