#!/usr/bin/env python3
"""
StreamAI Production Entry Point

This file serves as the main entry point for Railway deployment.
It imports and runs the Flask application from the obs directory.
"""

import os
import sys
from pathlib import Path

# Add the obs directory to the Python path
current_dir = Path(__file__).parent
obs_dir = current_dir / 'obs'
sys.path.insert(0, str(obs_dir))

# Import the Flask app and SocketIO instance
from api_server_production import app, socketio

if __name__ == '__main__':
    # Get port from environment variable (Railway sets this automatically)
    port = int(os.environ.get('PORT', 5001))
    
    # Set production environment - disable debug in production
    debug = False
    
    print(f"Starting StreamAI server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    
    # Run the application
    socketio.run(
        app, 
        debug=debug, 
        host='0.0.0.0', 
        port=port,
        allow_unsafe_werkzeug=True,  # Required for production with SocketIO
        log_output=True  # Enable logging for Railway
    )
