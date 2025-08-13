# src/routes/trade_signal_routes.py


from flask import Blueprint, jsonify, request

from algo_royale.services.db.trade_signal_repo import TradeSignalRepo

trade_signal_bp = Blueprint("trade_signal", __name__)
service = TradeSignalRepo()


@trade_signal_bp.route("/all", methods=["GET"])
def fetch_all_signals():
    signals = service.fetch_all_signals()
    return jsonify(signals)


@trade_signal_bp.route("/<symbol>", methods=["GET"])
def fetch_signals_by_symbol(symbol):
    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)
    signals = service.fetch_signals_by_symbol(symbol, limit, offset)
    return jsonify(signals)
