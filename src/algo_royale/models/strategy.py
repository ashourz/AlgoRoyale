from ml_model import train_model
import random

def pick_stock():
    """Choose the best stock for the day based on ML predictions & news sentiment."""
    candidates = ["AAPL", "TSLA", "NVDA"]
    best_stock = random.choice(candidates)  # Replace with ML-based selection
    return best_stock

def execute_trade():
    """Run the trading strategy using the best stock."""
    stock = pick_stock()
    train_model(stock)  # Retrain model nightly

    print(f"Buying {stock} at predicted low point...")
    # Simulate trade execution

execute_trade()
