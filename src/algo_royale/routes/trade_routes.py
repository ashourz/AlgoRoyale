# src/routes/trade_routes.py

from datetime import datetime

from flask import Blueprint, jsonify, request

from algo_royale.services.trades_service import TradesService


def create_trade_blueprint(service: TradesService) -> Blueprint:
    trade_bp = Blueprint("trade", __name__)

    @trade_bp.route("/unsettled", methods=["GET"])
    def fetch_unsettled_trades():
        limit = request.args.get("limit", default=10, type=int)
        offset = request.args.get("offset", default=0, type=int)
        trades = service.fetch_unsettled_trades(limit=limit, offset=offset)
        return jsonify(trades)

    @trade_bp.route("/date_range", methods=["GET"])
    def get_trades_by_date_range():
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        limit = request.args.get("limit", default=10, type=int)
        offset = request.args.get("offset", default=0, type=int)
        trades = service.fetch_trades_by_date_range(
            datetime.fromisoformat(start_date),
            datetime.fromisoformat(end_date),
            limit,
            offset,
        )
        return jsonify(trades)

    return trade_bp
