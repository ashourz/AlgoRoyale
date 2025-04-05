from flask import Flask, jsonify
import pandas as pd
from db import connect_db

app = Flask(__name__)

@app.route("/performance", methods=["GET"])
def get_performance():
    """Return recent trade performance."""
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM stock_data ORDER BY timestamp DESC LIMIT 10", conn)
    conn.close()
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
