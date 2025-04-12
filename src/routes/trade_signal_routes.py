# src/routes/trade_signal_routes.py

from flask import Blueprint, request, jsonify
from src.service.trade_signal_service import TradeSignalService
from datetime import datetime
from decimal import Decimal

trade_signal_bp = Blueprint("trade_signal", __name__)
service = TradeSignalService()

@trade_signal_bp.route("/", methods=["POST"])
def create_trade_signal():
    data = request.json
    service.create_signal(
        symbol=data["symbol"],
        signal=data["signal"],
        price=Decimal(data["price"]),
        created_at=datetime.fromisoformat(data["created_at"])
    )
    return jsonify({"message": "Trade signal created"}), 201

@trade_signal_bp.route("/<symbol>", methods=["GET"])
def get_signals_by_symbol(symbol):
    signals = service.get_signals_by_symbol(symbol)
    return jsonify(signals)

@trade_signal_bp.route("/id/<int:signal_id>", methods=["GET"])
def get_signal_by_id(signal_id):
    signal = service.get_signal_by_id(signal_id)
    return jsonify(signal)
