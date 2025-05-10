
from pathlib import Path
import sys
import streamlit.web.cli as stcli

def main():
    """Main function to run the Streamlit dashboard.
    This function sets up the command-line arguments and starts the Streamlit server.
    """
    try:
        dashboard_path = str(Path(__file__).parent / "dashboard.py")
        
        sys.argv = [
            "streamlit",
            "run",
            dashboard_path,
            "--server.port=8501",
            "--server.headless=false",
            "--browser.serverAddress=localhost"  # Critical change
        ]        
        stcli.main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except FileNotFoundError as e:
        print(f"File not found: {str(e)}")
    except ValueError as e:
        print(f"Value error: {str(e)}")
    except RuntimeError as e:
        print(f"Runtime error: {str(e)}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()