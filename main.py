from app import app
import signal
import sys
from types import FrameType
import threading
import webview
import time

def run_flask():
    """Run Flask app in a separate thread"""
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True, use_reloader=False)

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
            'http://127.0.0.1:5000',
            width=1200,
            height=800,
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
