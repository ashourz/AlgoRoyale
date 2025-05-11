# app_run.py

"""
App Runner for the Flask Application.

This script sets environment variables and runs the Flask app manually.

---------------------------------------------
How to Run the App:

Option 1 - Using Flask CLI (Recommended for Dev):
--------------------------------------------------
# On Unix/macOS:
export FLASK_APP=src.app
export FLASK_ENV=development
flask run

# On Windows (CMD):
set FLASK_APP=src.app
set FLASK_ENV=development
flask run

# On Windows (PowerShell):
$env:FLASK_APP="src.app"
$env:FLASK_ENV="development"
flask run

Option 2 - Using this Python script:
-------------------------------------
python app_run.py

This will:
1. Set the required environment variables.
2. Start the Flask development server.
---------------------------------------------
"""

import os
from algo_royale.logging.logger_singleton import Environment, LoggerSingleton, LoggerType
from src.app import app

logger = LoggerSingleton.get_instance(LoggerType.TRADING, Environment.PROD)

def set_environment_variables():
    """Sets Flask app and environment variables."""
    os.environ['FLASK_APP'] = 'src.app'
    os.environ['FLASK_ENV'] = 'development'
    logger.info("Environment variables set for Flask.")

if __name__ == "__main__":
    set_environment_variables()
    app.run(debug=True)
