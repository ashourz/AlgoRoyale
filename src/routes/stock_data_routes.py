# src/routes/stock_data_routes.py

from src.service.db.stock_data_service import StockDataService
from datetime import datetime
from decimal import Decimal
from flask import Blueprint, request, jsonify

trade_bp = Blueprint("stock_data", __name__)
service = StockDataService()

@trade_bp.route("/", methods=["POST"])
def create_stock_data():
    data = request.json
    service.create_stock_data(
        symbol=data["symbol"],
        open_price=Decimal(data["open_price"]),
        close_price=Decimal(data["close_price"]),
        high_price=Decimal(data["high_price"]),
        low_price=Decimal(data["low_price"]),
        volume=Decimal(data["volume"]),
        date=datetime.fromisoformat(data["date"])
    )
    return jsonify({"message": "Stock data created"}), 201

@trade_bp.route("/<string:symbol>", methods=["GET"])    
def get_stock_data_by_symbol(symbol):
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if start_date and end_date:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
        stock_data = service.get_stock_data_by_symbol_and_date(symbol, start_date, end_date)
    else:
        stock_data = service.get_stock_data_by_symbol(symbol)
    return jsonify(stock_data)


@trade_bp.route("/all", methods=["GET"])
def get_all_stock_data():
    stock_data = service.get_all_stock_data()
    return jsonify(stock_data)

@trade_bp.route("/update/<int:stock_data_id>", methods=["PUT"])
def update_stock_data(stock_data_id):
    data = request.json
    service.update_stock_data(
        stock_data_id=stock_data_id,
        symbol=data["symbol"],
        open_price=Decimal(data["open_price"]),
        close_price=Decimal(data["close_price"]),
        high_price=Decimal(data["high_price"]),
        low_price=Decimal(data["low_price"]),
        volume=Decimal(data["volume"]),
        date=datetime.fromisoformat(data["date"])
    )
    return jsonify({"message": "Stock data updated"})

@trade_bp.route("/delete/<int:stock_data_id>", methods=["DELETE"])
def delete_stock_data(stock_data_id):
    service.delete_stock_data(stock_data_id)
    return jsonify({"message": "Stock data deleted"})   

@trade_bp.route("/latest/<string:symbol>", methods=["GET"])
def get_latest_stock_data(symbol):
    stock_data = service.get_latest_stock_data(symbol)
    return jsonify(stock_data)


@trade_bp.route("/symbol_date", methods=["GET"])
def get_stock_data_by_symbol_and_date():
    symbol = request.args.get("symbol")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    stock_data = service.get_stock_data_by_symbol_and_date(symbol, datetime.fromisoformat(start_date), datetime.fromisoformat(end_date))
    return jsonify(stock_data)

