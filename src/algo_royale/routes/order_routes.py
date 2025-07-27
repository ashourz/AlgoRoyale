from flask import Blueprint, jsonify, request

from algo_royale.services.db.order_service import OrderService


def create_order_blueprint(service: OrderService) -> Blueprint:
    order_bp = Blueprint("order", __name__)

    @order_bp.route("/status/<string:status>", methods=["GET"])
    def fetch_orders_by_status(status: str):
        limit = request.args.get("limit", default=100, type=int)
        offset = request.args.get("offset", default=0, type=int)
        orders = service.fetch_orders_by_status(status, limit, offset)
        return jsonify(orders)

    @order_bp.route("/symbol/<string:symbol>/status/<string:status>", methods=["GET"])
    def fetch_orders_by_symbol_and_status(symbol: str, status: str):
        limit = request.args.get("limit", default=100, type=int)
        offset = request.args.get("offset", default=0, type=int)
        orders = service.fetch_orders_by_symbol_and_status(
            symbol, status, limit, offset
        )
        return jsonify(orders)

    @order_bp.route("/insert", methods=["POST"])
    def insert_order():
        data = request.json
        order_id = service.insert_order(
            symbol=data["symbol"],
            market=data["market"],
            order_type=data["order_type"],
            status=data["status"],
            action=data["action"],
            quantity=data["quantity"],
            price=data["price"],
            signal_id=data["signal_id"],
        )
        return jsonify({"order_id": order_id}), 201
