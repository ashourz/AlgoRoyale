import streamlit.web.cli as stcli
import sys
from pathlib import Path

def main():
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
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()