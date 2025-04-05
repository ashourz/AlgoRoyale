import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import pandas as pd
from db import connect_db

def get_training_data(symbol):
    """Retrieve stock data from PostgreSQL for model training."""
    conn = connect_db()
    df = pd.read_sql(f"SELECT * FROM stock_data WHERE symbol='{symbol}' ORDER BY timestamp", conn)
    conn.close()
    
    # Convert to numpy arrays
    data = df[['close']].values
    return data

def prepare_data(data, time_steps=50):
    """Prepare time series data for LSTM training."""
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:i+time_steps])
        y.append(data[i+time_steps])
    
    return np.array(X), np.array(y)

def build_model(input_shape):
    """Create an LSTM model."""
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    return model

def train_model(symbol):
    """Train the LSTM model using historical data."""
    data = get_training_data(symbol)
    X, y = prepare_data(data)
    
    model = build_model((X.shape[1], X.shape[2]))
    model.fit(X, y, epochs=10, batch_size=32)
    
    model.save(f"models/{symbol}_model.h5")
    print(f"Model for {symbol} saved.")

# Train on AAPL as example
if __name__ == "__main__":
    train_model("AAPL")
