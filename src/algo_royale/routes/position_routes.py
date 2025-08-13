from flask import Blueprint, jsonify, request

from algo_royale.services.positions_service import PositionsService


def create_position_blueprint(service: PositionsService) -> Blueprint:
    """
    Create a Flask blueprint for position routes.
    :param service: An instance of PositionsService.
    :return: A Flask blueprint with position routes.
    """
    position_bp = Blueprint("position", __name__)

    @position_bp.route("/positions", methods=["GET"])
    def fetch_all_positions():
        user_id = request.args.get("user_id")
        account_id = request.args.get("account_id")
        limit = request.args.get("limit", default=100, type=int)
        offset = request.args.get("offset", default=0, type=int)
        positions = service.fetch_all_positions(user_id, account_id, limit, offset)
        return jsonify(positions)

    return position_bp
