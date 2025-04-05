import configparser

# Load config.ini
config = configparser.ConfigParser()
config.read("config.ini")

# Access database settings
DB_HOST = config["database"]["host"]
DB_PORT = config["database"]["port"]
DB_NAME = config["database"]["dbname"]
DB_USER = config["database"]["user"]
DB_PASSWORD = config["database"]["password"]

# Access Alpaca API settings
ALPACA_API_KEY = config["alpaca"]["api_key"]
ALPACA_API_SECRET = config["alpaca"]["api_secret"]
ALPACA_BASE_URL = config["alpaca"]["base_url"]

# Access training settings
HISTORICAL_DAYS = int(config["training"]["historical_data_days"])
USE_LSTM = config["training"].getboolean("use_lstm")

# Access logging settings
LOG_FILE = config["logging"]["log_file"]

print(f"Connected to DB: {DB_NAME} on {DB_HOST}:{DB_PORT}")
print(f"Alpaca API Key: {ALPACA_API_KEY[:4]}********")  # Mask API Key for security
