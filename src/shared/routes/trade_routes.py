# src/routes/trade_routes.py

from shared.service.db.trade_service import TradeService
from datetime import datetime
from decimal import Decimal
from flask import Blueprint, request, jsonify

trade_bp = Blueprint("trade", __name__)
service = TradeService()

@trade_bp.route("/", methods=["POST"])
def create_trade():
    data = request.json
    service.create_trade(
        symbol=data["symbol"],
        entry_price=Decimal(data["entry_price"]),
        exit_price=Decimal(data["exit_price"]),
        quantity=Decimal(data["quantity"]),
        status=data["status"],
        created_at=datetime.fromisoformat(data["created_at"])
    )
    return jsonify({"message": "Trade created"}), 201

@trade_bp.route("/<int:trade_id>", methods=["PUT"])
def update_trade(trade_id):
    data = request.json
    service.update_trade(
        trade_id=trade_id,
        exit_price=Decimal(data["exit_price"]),
        exit_time=datetime.fromisoformat(data["exit_time"]),
        pnl=Decimal(data["pnl"])
    )
    return jsonify({"message": "Trade updated"}), 200

@trade_bp.route("/<int:trade_id>", methods=["GET"])
def get_trade_by_id(trade_id):
    trade = service.get_trade_by_id(trade_id)
    return jsonify(trade)

@trade_bp.route("/<string:symbol>", methods=["GET"])
def get_trades_by_symbol_with_limit(symbol):
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)
    trades = service.get_trades_by_symbol(symbol, limit, offset)
    return jsonify(trades)

@trade_bp.route("/history", methods=["GET"])
def get_trade_history():
    trades = service.get_trade_history()
    return jsonify(trades)

@trade_bp.route("/<int:trade_id>", methods=["DELETE"])
def delete_trade(trade_id):
    service.delete_trade(trade_id)
    return jsonify({"message": "Trade deleted"}), 200

@trade_bp.route("/open", methods=["GET"])
def get_open_trades():
    trades = service.get_open_trades()
    return jsonify(trades)

@trade_bp.route("/date_range", methods=["GET"])
def get_trades_by_date_range():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    trades = service.get_trades_by_date_range(datetime.fromisoformat(start_date), datetime.fromisoformat(end_date))
    return jsonify(trades)

@trade_bp.route("/symbol_date", methods=["GET"])
def get_trades_by_symbol_and_date():
    symbol = request.args.get("symbol")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    trades = service.get_trades_by_symbol_and_date(symbol, datetime.fromisoformat(start_date), datetime.fromisoformat(end_date))
    return jsonify(trades)

@trade_bp.route("/calculate_pnl", methods=["POST"])
def calculate_trade_pnl():
    data = request.json
    pnl = service.calculate_trade_pnl(
        entry_price=Decimal(data["entry_price"]),
        exit_price=Decimal(data["exit_price"]),
        shares=data["shares"]
    )
    return jsonify({"pnl": str(pnl)}), 200

