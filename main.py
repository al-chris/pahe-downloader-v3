import os
import sys

# --- Block to set Playwright browsers path when bundled ---
if getattr(sys, 'frozen', False):
    # This block of code will only run when the app is packaged by PyInstaller
    print("Running in bundled mode")
    
    # sys._MEIPASS is the path to the temporary folder where PyInstaller unpacks your app
    browsers_path = os.path.join(sys._MEIPASS, 'ms-playwright') # type: ignore
    
    # Set the environment variable for Playwright
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
    print(f"Set PLAYWRIGHT_BROWSERS_PATH to: {browsers_path}")
else:
    # This block will run when you run the script normally (e.g., `python main.py`)
    print("Running in development mode")

# --- End of Playwright browsers path block ---

from app import app
import signal
from types import FrameType
import threading
import webview
import time

def run_flask():
    """Run Flask app in a separate thread"""
    app.run(host='localhost', port=1523, debug=False, threaded=True, use_reloader=False)

def signal_handler(sig: int, frame: FrameType | None) -> None:
    """Handle graceful shutdown on Ctrl+C"""
    print('\n\nShutting down gracefully...')
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start Flask in a background thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Wait a moment for Flask to start
        time.sleep(2)
        
        # Create PyWebView window
        window = webview.create_window(  # type: ignore
            'Pahe Downloader',
            'http://localhost:1523',
            width=900,
            height=600,
            resizable=True,
            frameless=False
        )
        
        # Start the webview
        webview.start()
        
    except KeyboardInterrupt:
        print('\n\nShutting down gracefully...')
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
