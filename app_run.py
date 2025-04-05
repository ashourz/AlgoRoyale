import os
import subprocess
import sys

def install_flask():
    """
    Installs Flask if it's not already installed. Uses pip to install Flask
    via the command line.
    If the installation fails, an error message is displayed and the script stops.

    Raises:
        subprocess.CalledProcessError: If the installation fails.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask"])
    except subprocess.CalledProcessError:
        print("Error installing Flask. Please check your environment.")
        sys.exit(1)

def create_flask_app():
    """
    Creates a basic Flask application (`app.py`) in the current directory.
    The app responds with a simple JSON message when accessing the root endpoint.

    Creates the following basic Flask app:

    ```python
    from flask import Flask, jsonify

    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({"message": "Hello, World!"})

    if __name__ == '__main__':
        app.run(debug=True)
    ```
    """
    app_code = '''from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    with open("app.py", "w") as file:
        file.write(app_code)
    print("Flask app created as 'app.py'")

def set_environment_variables():
    """
    Sets the environment variables required for running the Flask application.
    
    This ensures that Flask knows which file to run (`FLASK_APP`) and 
    sets the environment mode to development (`FLASK_ENV`).
    
    On Windows, the script sets the necessary environment variables in 
    the current environment to run the Flask app.

    No manual setup of these variables is needed.
    """
    if os.name == 'nt':  # For Windows
        os.environ['FLASK_APP'] = 'AlgoRoyale.app'
        os.environ['FLASK_ENV'] = 'development'
    else:  # For macOS/Linux
        os.environ['FLASK_APP'] = 'AlgoRoyale.app'
        os.environ['FLASK_ENV'] = 'development'

    print("Environment variables set for Flask app.")

def run_flask_app():
    """
    Runs the Flask app after setting up the environment variables.

    The Flask application is launched by invoking `flask run` in the terminal.
    If an error occurs while running the app, the script will exit with an error message.

    The app will run at the default address: `http://127.0.0.1:5000`.
    """
    try:
        subprocess.check_call([sys.executable, '-m', 'flask', 'run'])
    except subprocess.CalledProcessError:
        print("Error running Flask app. Please check your environment.")
        sys.exit(1)

if __name__ == "__main__":
    """
    Main function to orchestrate the setup and running of the Flask app.
    
    This function:
    1. Installs Flask if it's not already installed.
    2. Creates the Flask app as 'app.py'.
    3. Sets the required environment variables for Flask.
    4. Runs the Flask app, allowing it to be accessed locally at
       'http://127.0.0.1:5000'.

    Instructions:
    1. Run this script by executing `python setup_and_run_flask_app.py` in your
       terminal.
    2. After running the script, open your web browser and go to 
       `http://127.0.0.1:5000` to view the Flask app.
    3. The app will return a JSON response: {"message": "Hello, World!"}
    """
    
    # Step 1: Install Flask if it's not already installed
    install_flask()

    # Step 2: Create a simple Flask app in 'app.py'
    #create_flask_app()

    # Step 3: Set up the required environment variables for Flask to run
    set_environment_variables()

    # Step 4: Run the Flask app
    #run_flask_app()
