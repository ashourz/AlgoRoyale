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
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if start_date and end_date:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
        signals = service.get_signal_by_symbol_and_date(symbol, start_date, end_date)
    else:
        signals = service.get_signals_by_symbol(symbol)
    return jsonify(signals)

@trade_signal_bp.route("/id/<int:signal_id>", methods=["GET"])
def get_signal_by_id(signal_id):
    signal = service.get_signal_by_id(signal_id)
    return jsonify(signal)

@trade_signal_bp.route("/all", methods=["GET"])
def get_all_signals():
    signals = service.get_all_signals()
    return jsonify(signals)

@trade_signal_bp.route("/update/<int:signal_id>", methods=["PUT"])
def update_trade_signal(signal_id):
    data = request.json
    service.update_signal(
        signal_id=signal_id,
        symbol=data["symbol"],
        signal=data["signal"],
        price=Decimal(data["price"]),
        created_at=datetime.fromisoformat(data["created_at"])
    )
    return jsonify({"message": "Trade signal updated"})

@trade_signal_bp.route("/delete/<int:signal_id>", methods=["DELETE"])
def delete_trade_signal(signal_id):
    service.delete_signal(signal_id)
    return jsonify({"message": "Trade signal deleted"})
