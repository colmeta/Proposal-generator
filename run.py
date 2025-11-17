"""
Entry point for Render deployment
This ensures the Flask app starts correctly
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import and start the app
from api.endpoints import app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    host = '0.0.0.0'
    
    logger.info(f"Starting Flask app from run.py on {host}:{port}")
    logger.info(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
    
    app.run(host=host, port=port, debug=False, threaded=True)

