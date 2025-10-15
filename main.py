from app import app, browser_manager
import signal
import sys
from types import FrameType

def signal_handler(sig: int, frame: FrameType | None) -> None:
    """Handle graceful shutdown on Ctrl+C"""
    print('\n\nShutting down gracefully...')
    try:
        browser_manager.cleanup()
    except Exception as e:
        print(f"Error during cleanup: {e}")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Use threaded=True for better Windows compatibility
        # use_reloader=False prevents the double-process issue with debug mode
        app.run(debug=True, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print('\n\nShutting down gracefully...')
        browser_manager.cleanup()
        sys.exit(0)
