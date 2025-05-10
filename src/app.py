# src/app.py

from flask import Flask
from algo_royale.routes.trade_signal_routes import trade_signal_bp
from algo_royale.routes.trade_routes import trade_bp
from algo_royale.routes.indicator_routes import indicator_bp

def create_app():
    """
    Factory method to create and configure the Flask app.
    """
    app = Flask(__name__)

    # Register Blueprints
    app.register_blueprint(trade_signal_bp, url_prefix="/api/trade-signals")
    app.register_blueprint(trade_bp, url_prefix="/api/trades")
    app.register_blueprint(indicator_bp, url_prefix="/api/indicators")

    @app.route("/")
    def index():
        return {"message": "Welcome to the Algo Royale API!"}

    return app

# Only run the app if this file is executed directly (not during imports)
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
