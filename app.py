import threading
import time
import sys
import os

try:
    import webview
except ImportError:
    print("pywebview is not installed. Run: pip install pywebview")
    sys.exit(1)

import server

def start_server():
    server.print(f"[STARTUP] Mission Control SaaS Server starting on http://localhost:{server.PORT}", flush=True)
    httpd = server.HTTPServer(("127.0.0.1", server.PORT), server.MissionControlHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    # Start the backend server in a daemon thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait a moment to ensure server is up
    time.sleep(1)

    # Create the native desktop window pointing to our local server
    webview.create_window(
        'Mission Control - Antigravity', 
        f'http://127.0.0.1:{server.PORT}',
        width=1280,
        height=800,
        min_size=(1024, 768),
        background_color='#111113' # Match the dark theme background
    )
    
    # Start the GUI loop
    webview.start(private_mode=False)
